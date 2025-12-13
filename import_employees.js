const fs = require('fs');
const https = require('https');
const http = require('http');

// Read the CSV file
const csvData = fs.readFileSync('/Users/maiwand/INARA-HR/final.csv', 'utf-8');

// Parse CSV
function parseCSV(text) {
  const lines = text.split('\n').filter(line => line.trim());
  if (lines.length < 2) return [];

  const headers = lines[0].split(',');
  const employees = [];

  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]);
    if (values.length === 0) continue;

    const employee = {};
    headers.forEach((header, index) => {
      const value = values[index]?.trim() || '';
      
      switch (header.trim()) {
        case 'First Name':
          employee.first_name = value;
          break;
        case 'Last Name':
          employee.last_name = value;
          break;
        case 'Work Email':
          employee.work_email = value;
          break;
        case 'Phone':
          employee.phone = value;
          break;
        case 'Mobile':
          employee.mobile = value;
          break;
        case 'Date of Birth (YYYY-MM-DD)':
          employee.date_of_birth = convertDate(value);
          break;
        case 'Gender (male/female/other)':
          employee.gender = value.toLowerCase();
          break;
        case 'Nationality (Country Code)':
          employee.nationality = value;
          break;
        case 'Employment Type (full_time/part_time/consultant/volunteer)':
          employee.employment_type = value.toLowerCase().replace(' ', '_');
          break;
        case 'Work Location':
          employee.work_location = value;
          break;
        case 'Hire Date (YYYY-MM-DD)':
          employee.hire_date = convertDate(value);
          break;
        case 'Position/Title':
          employee.position = value;
          break;
        case 'Department':
          employee.department = value;
          break;
        case 'Employee Number':
          employee.employee_number = value;
          break;
      }
    });

    // Only add if we have required fields
    if (employee.first_name && employee.last_name && employee.work_email) {
      employees.push(employee);
    }
  }

  return employees;
}

function parseCSVLine(line) {
  const values = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      values.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  
  values.push(current);
  return values;
}

function convertDate(dateStr) {
  if (!dateStr || dateStr.trim() === '') return null;
  
  // Handle DD/MM/YYYY format
  if (dateStr.includes('/')) {
    const parts = dateStr.split('/');
    if (parts.length === 3) {
      const day = parts[0].padStart(2, '0');
      const month = parts[1].padStart(2, '0');
      const year = parts[2].length === 2 ? '20' + parts[2] : parts[2];
      return `${year}-${month}-${day}`;
    }
  }
  
  return dateStr;
}

async function importEmployee(employee, token) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(employee);
    
    const options = {
      hostname: 'localhost',
      port: 8000,
      path: '/api/v1/employees/',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Content-Length': data.length
      }
    };

    const req = http.request(options, (res) => {
      let responseData = '';

      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        if (res.statusCode === 200 || res.statusCode === 201) {
          resolve({ success: true, data: responseData });
        } else {
          resolve({ success: false, error: responseData, status: res.statusCode });
        }
      });
    });

    req.on('error', (error) => {
      resolve({ success: false, error: error.message });
    });

    req.write(data);
    req.end();
  });
}

async function main() {
  // You need to replace this with your actual access token
  const token = process.argv[2];
  
  if (!token) {
    console.error('Usage: node import_employees.js <access_token>');
    console.error('\nTo get your access token:');
    console.error('1. Log in to the INARA HR system');
    console.error('2. Open browser console (F12)');
    console.error('3. Type: localStorage.getItem("access_token")');
    console.error('4. Copy the token and run: node import_employees.js <token>');
    process.exit(1);
  }

  console.log('Parsing CSV file...');
  const employees = parseCSV(csvData);
  console.log(`Found ${employees.length} employees to import\n`);

  let successCount = 0;
  let failedCount = 0;
  const errors = [];

  for (let i = 0; i < employees.length; i++) {
    const employee = employees[i];
    process.stdout.write(`[${i + 1}/${employees.length}] Importing ${employee.first_name} ${employee.last_name}...`);
    
    const result = await importEmployee(employee, token);
    
    if (result.success) {
      successCount++;
      console.log(' ✓');
    } else {
      failedCount++;
      console.log(' ✗');
      errors.push({
        name: `${employee.first_name} ${employee.last_name}`,
        email: employee.work_email,
        error: result.error,
        status: result.status
      });
    }
    
    // Small delay to avoid overwhelming the server
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  console.log('\n' + '='.repeat(50));
  console.log('Import Summary:');
  console.log(`✓ Successful: ${successCount}`);
  console.log(`✗ Failed: ${failedCount}`);
  console.log('='.repeat(50));

  if (errors.length > 0) {
    console.log('\nErrors:');
    errors.forEach((err, idx) => {
      console.log(`\n${idx + 1}. ${err.name} (${err.email})`);
      console.log(`   Status: ${err.status}`);
      console.log(`   Error: ${err.error.substring(0, 200)}`);
    });
  }
}

main().catch(console.error);
