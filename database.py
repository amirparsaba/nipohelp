import asyncpg
from config import DB_CONFIG, DEBUG

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(**DB_CONFIG, min_size=2, max_size=10)
            print("✅ اتصال به دیتابیس برقرار شد")
        except Exception as e:
            print(f"❌ خطا در اتصال به دیتابیس: {e}")
            raise e
        await self._create_tables()

    async def _create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    icon TEXT DEFAULT '📁'
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS subcategories (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    cat_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
                    icon TEXT DEFAULT '📌',
                    UNIQUE(name, cat_id)
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS links (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    description TEXT,
                    subcat_id INTEGER REFERENCES subcategories(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    category_name TEXT NOT NULL,
                    subcategory_name TEXT NOT NULL,
                    link TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    admin_msg_id BIGINT,
                    admin_note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await self._insert_default_data()

    async def _insert_default_data(self):
        async with self.pool.acquire() as conn:
            default_cats = [('برنامه‌نویسی', '💻'), ('هنر', '🎨'), ('ویدیو', '🎬'), ('گرافیک', '🖌️')]
            for name, icon in default_cats:
                await conn.execute("INSERT INTO categories (name, icon) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING", name, icon)

            cats = await conn.fetch("SELECT id, name FROM categories")
            cat_map = {r['name']: r['id'] for r in cats}

            default_subs = [
                ('پایتون', cat_map.get('برنامه‌نویسی'), '🐍'),
                ('جاوااسکریپت', cat_map.get('برنامه‌نویسی'), '📜'),
                ('نقاشی', cat_map.get('هنر'), '🎨'),
                ('تدوین', cat_map.get('ویدیو'), '✂️'),
                ('فتوشاپ', cat_map.get('گرافیک'), '📷')
            ]
            for name, cat_id, icon in default_subs:
                if cat_id:
                    await conn.execute("INSERT INTO subcategories (name, cat_id, icon) VALUES ($1, $2, $3) ON CONFLICT (name, cat_id) DO NOTHING", name, cat_id, icon)

    async def get_categories(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT id, name, icon FROM categories ORDER BY id")

    async def get_subcategories(self, cat_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT id, name, icon FROM subcategories WHERE cat_id=$1 ORDER BY name", cat_id)

    async def get_links(self, subcat_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT id, title, url, description FROM links WHERE subcat_id=$1 ORDER BY created_at DESC", subcat_id)

    async def save_request(self, user_id, username, first_name, last_name, category, subcategory, link, description):
        async with self.pool.acquire() as conn:
            rid = await conn.fetchval('''
                INSERT INTO requests (user_id, username, first_name, last_name, category_name, subcategory_name, link, description)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id
            ''', user_id, username, first_name, last_name, category, subcategory, link, description)
            return rid

    async def update_request_msg_id(self, rid, msg_id):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE requests SET admin_msg_id=$1 WHERE id=$2", msg_id, rid)

    async def get_request(self, rid):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM requests WHERE id=$1", rid)

    async def get_pending_requests(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM requests WHERE status='pending' ORDER BY created_at ASC")

    async def approve_request(self, rid, note=None):
        async with self.pool.acquire() as conn:
            req = await conn.fetchrow("SELECT * FROM requests WHERE id=$1", rid)
            if not req:
                return False

            cat_id = await conn.fetchval("SELECT id FROM categories WHERE name=$1", req['category_name'])
            if not cat_id:
                cat_id = await conn.fetchval("INSERT INTO categories (name) VALUES ($1) RETURNING id", req['category_name'])

            sub_id = await conn.fetchval("SELECT id FROM subcategories WHERE name=$1 AND cat_id=$2", req['subcategory_name'], cat_id)
            if not sub_id:
                sub_id = await conn.fetchval("INSERT INTO subcategories (name, cat_id) VALUES ($1, $2) RETURNING id", req['subcategory_name'], cat_id)

            title = f"{req['subcategory_name']} - منبع مفید"
            await conn.execute("INSERT INTO links (title, url, description, subcat_id) VALUES ($1, $2, $3, $4)", title, req['link'], req['description'], sub_id)
            await conn.execute("UPDATE requests SET status='approved', admin_note=$2 WHERE id=$1", rid, note)
            return True

    async def reject_request(self, rid, note=None):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE requests SET status='rejected', admin_note=$2 WHERE id=$1", rid, note)
            return True

db = Database()