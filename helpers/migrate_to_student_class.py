"""
Migration script untuk refactoring ke Student Class system.
Menambahkan tabel student_class, update kelas_enrollment dan jadwal.

PERHATIAN: Backup database sebelum menjalankan script ini!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from database import DATABASE_URL
from models import Base, StudentClass

async def migrate_to_student_class():
    """
    Migration steps:
    1. Create student_class table
    2. Create default student class
    3. Add student_class_id to kelas_enrollment (keep old kelas_id for now)
    4. Add student_class_id to jadwal
    5. Migrate existing data to default class
    """
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        print("\n🔄 Step 1: Creating student_class table...")
        await conn.run_sync(Base.metadata.create_all, tables=[StudentClass.__table__])
        
        print("\n🔄 Step 2: Creating DEFAULT_CLASS...")
        await conn.execute(text("""
            INSERT INTO student_class (class_name, created_at)
            VALUES ('DEFAULT_CLASS', NOW())
            ON CONFLICT (class_name) DO NOTHING
        """))
        
        print("\n🔄 Step 3: Adding student_class_id to kelas_enrollment...")
        # Check if column exists
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='kelas_enrollment' AND column_name='student_class_id'
        """))
        if not result.fetchone():
            await conn.execute(text("""
                ALTER TABLE kelas_enrollment 
                ADD COLUMN student_class_id INTEGER
            """))
            print("   ✅ Added student_class_id column")
        else:
            print("   ℹ️  Column already exists")
        
        print("\n🔄 Step 4: Migrating enrollment data to DEFAULT_CLASS...")
        await conn.execute(text("""
            UPDATE kelas_enrollment 
            SET student_class_id = (SELECT class_id FROM student_class WHERE class_name = 'DEFAULT_CLASS')
            WHERE student_class_id IS NULL
        """))
        
        print("\n🔄 Step 5: Adding student_class_id to jadwal...")
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='jadwal' AND column_name='student_class_id'
        """))
        if not result.fetchone():
            await conn.execute(text("""
                ALTER TABLE jadwal 
                ADD COLUMN student_class_id INTEGER
            """))
            print("   ✅ Added student_class_id column to jadwal")
        else:
            print("   ℹ️  Column already exists in jadwal")
        
        print("\n🔄 Step 6: Migrating jadwal data to DEFAULT_CLASS...")
        await conn.execute(text("""
            UPDATE jadwal 
            SET student_class_id = (SELECT class_id FROM student_class WHERE class_name = 'DEFAULT_CLASS')
            WHERE student_class_id IS NULL
        """))
        
        print("\n🔄 Step 7: Making student_class_id NOT NULL...")
        await conn.execute(text("""
            ALTER TABLE kelas_enrollment 
            ALTER COLUMN student_class_id SET NOT NULL
        """))
        await conn.execute(text("""
            ALTER TABLE jadwal 
            ALTER COLUMN student_class_id SET NOT NULL
        """))
        
        print("\n🔄 Step 8: Adding foreign key constraints...")
        try:
            await conn.execute(text("""
                ALTER TABLE kelas_enrollment 
                ADD CONSTRAINT fk_enrollment_student_class 
                FOREIGN KEY (student_class_id) REFERENCES student_class(class_id)
            """))
        except Exception as e:
            print(f"   ℹ️  Foreign key might already exist: {e}")
        
        try:
            await conn.execute(text("""
                ALTER TABLE jadwal 
                ADD CONSTRAINT fk_jadwal_student_class 
                FOREIGN KEY (student_class_id) REFERENCES student_class(class_id)
            """))
        except Exception as e:
            print(f"   ℹ️  Foreign key might already exist: {e}")
        
        print("\n🔄 Step 9: Optional - Drop old kelas_id from kelas_enrollment...")
        print("   ⚠️  SKIPPED - Keeping kelas_id for safety. Remove manually if needed.")
        # await conn.execute(text("ALTER TABLE kelas_enrollment DROP COLUMN kelas_id"))
    
    await engine.dispose()
    print("\n✅ Migration completed successfully!")
    print("\n📊 Summary:")
    print("   - Created student_class table")
    print("   - Created DEFAULT_CLASS for existing data")
    print("   - Added student_class_id to kelas_enrollment and jadwal")
    print("   - All existing enrollments and jadwal assigned to DEFAULT_CLASS")
    print("\n🎯 Next steps:")
    print("   1. Test the application")
    print("   2. Create real student classes (A11.4109, etc)")
    print("   3. Re-assign students to correct classes")
    print("   4. Update jadwal to use correct student classes")

if __name__ == "__main__":
    print("="*60)
    print("STUDENT CLASS MIGRATION SCRIPT")
    print("="*60)
    print("\n⚠️  WARNING: This will modify your database!")
    print("Make sure you have a backup before proceeding.\n")
    
    confirm = input("Type 'YES' to continue: ")
    if confirm == "YES":
        asyncio.run(migrate_to_student_class())
    else:
        print("❌ Migration cancelled")
