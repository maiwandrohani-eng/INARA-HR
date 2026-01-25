"""Check leave balances in database"""
import os
import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def check_balances():
    if 'DATABASE_URL' not in os.environ:
        print("ERROR: DATABASE_URL not set")
        return
        
    engine = create_async_engine(os.environ['DATABASE_URL'])
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check leave balances
        result = await session.execute(
            text('SELECT employee_id, leave_type, year, total_days, used_days, available_days FROM leave_balances ORDER BY employee_id, leave_type;')
        )
        rows = result.fetchall()
        
        if not rows:
            print('❌ No leave balances found in database')
            print('\nChecking leave policies...')
            
            # Check leave policies
            policies_result = await session.execute(
                text('SELECT id, name, leave_type, days_per_year, accrual_rate FROM leave_policies;')
            )
            policies = policies_result.fetchall()
            
            if policies:
                print(f'\n✅ Found {len(policies)} leave policies:')
                for policy in policies:
                    print(f'  - {policy[1]}: {policy[2]} - {policy[3]} days/year - Accrual: {policy[4]}')
                
                print('\n⚠️  Leave policies exist but no employee balances initialized!')
                print('You need to initialize leave balances for employees.')
            else:
                print('❌ No leave policies found either')
        else:
            print(f'✅ Found {len(rows)} leave balances:\n')
            print('Employee ID                          | Type   | Year | Total | Used | Available')
            print('-' * 90)
            for row in rows:
                print(f'{row[0]} | {row[1]:6} | {row[2]} | {row[3]:5} | {row[4]:4} | {row[5]:9}')
    
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(check_balances())
