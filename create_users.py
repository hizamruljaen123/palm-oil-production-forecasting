"""
Script untuk membuat user baru dengan password yang di-hash (MD5)
Jalankan script ini untuk membuat user admin dan user biasa
"""

import hashlib
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'data_air'
}

def create_default_users():
    """Membuat user default (admin dan user biasa)"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Hash passwords with MD5
        # admin -> 21232f297a57a5a743894a0e4a801fc3
        admin_password = hashlib.md5('admin'.encode()).hexdigest()
        # user -> ee11cbb19052e40b07aac0ca060c23ee
        user_password = hashlib.md5('user'.encode()).hexdigest()
        
        # Create admin user
        try:
            cursor.execute("""
                INSERT INTO users (username, password, role, full_name)
                VALUES (%s, %s, %s, %s)
            """, ('admin', admin_password, 'admin', 'Administrator'))
            print("✓ Admin user created successfully")
        except mysql.connector.IntegrityError:
            print("! Admin user already exists")
            # Update password if exists to ensure it matches
            cursor.execute("UPDATE users SET password = %s WHERE username = 'admin'", (admin_password,))
            print("  - Password updated")
        
        # Create regular user
        try:
            cursor.execute("""
                INSERT INTO users (username, password, role, full_name)
                VALUES (%s, %s, %s, %s)
            """, ('user', user_password, 'user', 'Regular User'))
            print("✓ Regular user created successfully")
        except mysql.connector.IntegrityError:
            print("! Regular user already exists")
            # Update password if exists to ensure it matches
            cursor.execute("UPDATE users SET password = %s WHERE username = 'user'", (user_password,))
            print("  - Password updated")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "="*50)
        print("Default users (MD5):")
        print("="*50)
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin")
        print("  Role: admin")
        print("\nRegular User:")
        print("  Username: user")
        print("  Password: user")
        print("  Role: user")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")

def create_custom_user():
    """Membuat user custom dengan input dari terminal"""
    print("\n" + "="*50)
    print("Create Custom User")
    print("="*50)
    
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    full_name = input("Full Name: ").strip()
    role = input("Role (admin/user) [user]: ").strip() or 'user'
    
    if role not in ['admin', 'user']:
        print("Invalid role. Using 'user' as default.")
        role = 'user'
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO users (username, password, role, full_name)
            VALUES (%s, %s, %s, %s)
        """, (username, hashed_password, role, full_name))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✓ User '{username}' created successfully!")
        print(f"  Role: {role}")
        print(f"  Full Name: {full_name}")
        
    except mysql.connector.IntegrityError:
        print(f"\n✗ Error: Username '{username}' already exists!")
    except Exception as e:
        print(f"\n✗ Error: {e}")

def list_users():
    """Menampilkan daftar semua user"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, username, role, full_name, created_at FROM users ORDER BY id")
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*70)
        print("List of Users")
        print("="*70)
        print(f"{'ID':<5} {'Username':<15} {'Role':<10} {'Full Name':<20} {'Created':<15}")
        print("-"*70)
        
        for user in users:
            print(f"{user['id']:<5} {user['username']:<15} {user['role']:<10} {user['full_name'] or '-':<20} {str(user['created_at'])[:10]:<15}")
        
        print("="*70)
        print(f"Total users: {len(users)}")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Menu utama"""
    while True:
        print("\n" + "="*50)
        print("User Management System")
        print("="*50)
        print("1. Create default users (admin & user)")
        print("2. Create custom user")
        print("3. List all users")
        print("4. Exit")
        print("="*50)
        
        choice = input("Choose option (1-4): ").strip()
        
        if choice == '1':
            create_default_users()
        elif choice == '2':
            create_custom_user()
        elif choice == '3':
            list_users()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1-4.")

if __name__ == '__main__':
    main()
