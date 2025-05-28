## Database Setup & Usage

### 1. Prerequisites

- Ensure you have a supported database installed (e.g., PostgreSQL, MySQL, SQLite).
- Install required Python dependencies:
  ```
  pip install -r requirements.txt
  ```

### 2. Configuration

- Copy `.env.example` to `.env` and add your database credentials:
  ```
 GOOGLE_API_KEY=your-google-api-key-here
 ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key-here
  ```
- Never commit your real `.env` file to git.

### 3. Database Initialization

- If migrations are used, run the migration tool (e.g., Alembic, Django, Flask-Migrate) to create tables:
  ```
  # Example for Alembic
  alembic upgrade head
  ```

- Alternatively, run the provided initialization script if available:
  ```
  python scripts/init_db.py
  ```

### 4. Usage in the Project

- The application will automatically connect to the database using the credentials from your `.env` file.
- Database models and queries are managed in the `models/` or `database/` directory (adjust as per your project structure).
- Example usage in code:
  ```python
  from configs.settings import get_db_session

  session = get_db_session()
  result = session.execute("SELECT 1")
  ```

### 5. Troubleshooting

- Ensure your database server is running and accessible.
- Double-check your `.env` configuration for typos.
- Check logs for connection errors.

---

For more details, see the [configs](configs/) directory and any database-related scripts in the project.