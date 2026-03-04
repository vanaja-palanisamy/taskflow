# PostgreSQL Setup

1. Install PostgreSQL and create a database.
2. Set the `DATABASE_URL` environment variable in your system or `.env` file. Example:
   
	```
	postgresql://username:password@localhost:5432/dbname
	```
3. (Recommended) Install the [PostgreSQL extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-postgresql) for easy database management inside VS Code.

4. Remove any old SQLite files from `instance/` (already done).

5. Run the app:
	```
	python app.py
	```
# taskflow-v1