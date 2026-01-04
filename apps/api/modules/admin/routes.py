"""
Admin Routes
Administrative functions and system management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from io import BytesIO
import os
import re
import uuid

from core.database import get_db
from core.dependencies import get_current_user
from core.pdf_generator import create_user_manual_pdf
from modules.auth.models import User, Role

router = APIRouter(tags=["admin"])


@router.get("/user-manual")
async def get_user_manual(
    current_user: dict = Depends(get_current_user)
):
    """
    Get the user manual in HTML format
    """
    # Calculate path to USER_MANUAL.md
    # The file is in the API directory (apps/api/USER_MANUAL.md)
    # In Docker: /app/USER_MANUAL.md
    # Local: apps/api/USER_MANUAL.md (relative to project root)
    current_dir = os.path.dirname(__file__)  # apps/api/modules/admin
    modules_dir = os.path.dirname(current_dir)  # apps/api/modules
    api_dir = os.path.dirname(modules_dir)  # apps/api
    manual_path = os.path.join(api_dir, "USER_MANUAL.md")
    
    # Return HTML version
    try:
        if not os.path.exists(manual_path):
            raise HTTPException(status_code=404, detail=f"User manual not found at: {manual_path}")
        
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_content = f.read()
        
        # Convert markdown to HTML (simple conversion)
        html_content = markdown_to_html(manual_content)
        
        return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"User manual file not found at: {manual_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading manual: {str(e)}")


def markdown_to_html(markdown_text: str) -> str:
    """Simple markdown to HTML converter"""
    import re
    
    html = markdown_text
    
    # Headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(\d+)\. (.+)$', r'<li>\2</li>', html, flags=re.MULTILINE)
    
    # Wrap consecutive list items in <ul>
    html = re.sub(r'(<li>.*?</li>\n?)+', lambda m: '<ul>' + m.group(0) + '</ul>', html, flags=re.DOTALL)
    
    # Paragraphs (lines that aren't already HTML)
    lines = html.split('\n')
    result = []
    in_paragraph = False
    
    for line in lines:
        if line.strip() == '':
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append('')
        elif line.startswith('<'):
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)
        else:
            if not in_paragraph:
                result.append('<p>')
                in_paragraph = True
            result.append(line)
    
    if in_paragraph:
        result.append('</p>')
    
    html = '\n'.join(result)
    
    # Wrap in HTML document
    html_doc = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>INARA HR Management System - User Manual</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }}
            h1 {{
                color: #1a1a1a;
                border-bottom: 3px solid #e91e63;
                padding-bottom: 10px;
                margin-top: 30px;
            }}
            h2 {{
                color: #2c3e50;
                margin-top: 30px;
                padding-top: 10px;
                border-top: 1px solid #eee;
            }}
            h3 {{
                color: #34495e;
                margin-top: 20px;
            }}
            ul, ol {{
                margin-left: 20px;
                margin-bottom: 15px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            p {{
                margin-bottom: 15px;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            .download-pdf {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #e91e63;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .download-pdf:hover {{
                background-color: #c2185b;
            }}
        </style>
    </head>
    <body>
        <div style="text-align: center; margin-bottom: 30px;">
            <h1>INARA HR Management System</h1>
            <h2>User Manual</h2>
            <p>Version 1.0 | Last Updated: January 2026</p>
            <a href="/api/v1/admin/user-manual?format=pdf" class="download-pdf">📥 Download PDF Version</a>
        </div>
        {html}
    </body>
    </html>
    """
    
    return html_doc


@router.post("/fix-my-roles")
async def fix_my_roles(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fix admin/ceo roles for the current user (maiwand@inara.org only, or users who can't access admin)
    This endpoint helps recover admin access if roles are missing.
    """
    user_email = current_user.get("email", "")
    
    # Only allow fixing maiwand@inara.org or if user already has some admin access
    if user_email != "maiwand@inara.org" and not any(role in current_user.get("roles", []) for role in ["admin", "ceo", "super_admin"]):
        raise HTTPException(
            status_code=403,
            detail="This endpoint can only be used by maiwand@inara.org or existing admins"
        )
    
    try:
        # Get the user from database
        result = await db.execute(
            select(User).where(User.email == user_email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Ensure admin, ceo, and super_admin roles exist
        roles_to_ensure = ["super_admin", "admin", "ceo"]
        existing_roles = {}
        
        for role_name in roles_to_ensure:
            result = await db.execute(
                select(Role).where(Role.name == role_name)
            )
            role = result.scalar_one_or_none()
            
            if not role:
                role_display = {
                    "super_admin": "Super Administrator",
                    "admin": "Administrator",
                    "ceo": "Chief Executive Officer"
                }.get(role_name, role_name.replace('_', ' ').title())
                
                role = Role(
                    id=uuid.uuid4(),
                    name=role_name,
                    display_name=role_display,
                    description=f"{role_display} access",
                    is_system=True
                )
                db.add(role)
                await db.flush()
            
            existing_roles[role_name] = role
        
        # Add missing roles to the user
        user_current_role_names = {r.name for r in user.roles}
        roles_added = []
        
        for role_name in ["admin", "ceo", "super_admin"]:
            if role_name not in user_current_role_names:
                user.roles.append(existing_roles[role_name])
                roles_added.append(role_name)
        
        if roles_added:
            await db.commit()
            await db.refresh(user, ["roles"])
            
            return {
                "success": True,
                "message": f"Added roles: {', '.join(roles_added)}",
                "user_email": user_email,
                "roles": [r.name for r in user.roles]
            }
        else:
            return {
                "success": True,
                "message": "User already has all required roles",
                "user_email": user_email,
                "roles": [r.name for r in user.roles]
            }
            
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error fixing roles: {str(e)}")
