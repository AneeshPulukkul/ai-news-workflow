# Database Schema Documentation: Agentic News Workflow System

This document provides detailed information about the database schemas used in the Agentic News Workflow System. Understanding these schemas is essential for developers who need to query, modify, or extend the system's data storage.

## 1. Overview

The system uses two SQLite databases to store different types of data:

1. **News Database**: Stores scraped news articles and their metadata
2. **Content Database**: Stores AI-generated content and its approval status

## 2. News Database Schema

The News Database (`data/news_database.db`) stores all scraped articles from various sources.

### 2.1 Table: `articles`

This table stores all scraped news articles and their metadata.

#### 2.1.1 Schema Definition

```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT UNIQUE,
    source TEXT,
    category TEXT,
    published_date TEXT,
    scraped_date TEXT,
    keywords TEXT,
    summary TEXT
);

CREATE INDEX idx_scraped_date ON articles(scraped_date);
CREATE INDEX idx_category ON articles(category);
CREATE UNIQUE INDEX idx_url ON articles(url);
```

#### 2.1.2 Field Descriptions

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | INTEGER | Unique identifier for the article | Primary key, auto-incrementing |
| `title` | TEXT | Article title | Not null |
| `content` | TEXT | Full article content | May be null if only metadata is available |
| `url` | TEXT | Original article URL | Unique across the table |
| `source` | TEXT | Name of the source (e.g., "TechCrunch") | - |
| `category` | TEXT | Article category (e.g., "technology") | - |
| `published_date` | TEXT | Original publication date (ISO format) | - |
| `scraped_date` | TEXT | Date when the article was scraped (ISO format) | - |
| `keywords` | TEXT | JSON array of keywords extracted from the article | Stored as JSON string |
| `summary` | TEXT | Article summary (generated or extracted) | - |

#### 2.1.3 Indexes

- **Primary Key Index**: On `id` (automatically created)
- **Unique Index**: On `url` to prevent duplicate articles
- **Performance Index**: On `scraped_date` for date-based filtering
- **Performance Index**: On `category` for category-based filtering

#### 2.1.4 Example Data

```
id | title                     | content                   | url                           | source      | category    | published_date       | scraped_date         | keywords                           | summary
---|---------------------------|---------------------------|-------------------------------|-------------|-------------|----------------------|----------------------|------------------------------------|---------------------------
1  | AI Breakthrough in Health | <article content>         | https://techcrunch.com/ai-... | TechCrunch  | technology  | 2023-08-01T14:30:00Z | 2023-08-01T15:45:32Z | ["AI", "healthcare", "ML"]         | AI is transforming healthcare...
2  | New Quantum Computing... | <article content>         | https://wired.com/quantum-... | Wired       | technology  | 2023-08-01T10:15:00Z | 2023-08-01T15:46:10Z | ["quantum", "computing", "physics"] | Researchers demonstrate new...
```

### 2.2 Common Queries

#### 2.2.1 Get Recent Articles by Category

```sql
SELECT id, title, source, published_date, summary 
FROM articles 
WHERE category = ? AND date(scraped_date) >= date('now', '-7 days') 
ORDER BY published_date DESC;
```

#### 2.2.2 Get Articles by Keyword

```sql
SELECT id, title, source, published_date 
FROM articles 
WHERE keywords LIKE ? 
ORDER BY published_date DESC;
```

#### 2.2.3 Get Article Count by Source

```sql
SELECT source, COUNT(*) as article_count 
FROM articles 
GROUP BY source 
ORDER BY article_count DESC;
```

## 3. Content Database Schema

The Content Database (`data/content_database.db`) stores all AI-generated content and its approval status.

### 3.1 Table: `generated_articles`

This table stores AI-generated articles based on scraped news.

#### 3.1.1 Schema Definition

```sql
CREATE TABLE generated_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    category TEXT,
    source_articles TEXT,
    generated_date TEXT,
    status TEXT DEFAULT 'pending',
    feedback TEXT,
    edited_content TEXT
);

CREATE INDEX idx_status ON generated_articles(status);
CREATE INDEX idx_generated_date ON generated_articles(generated_date);
```

#### 3.1.2 Field Descriptions

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | INTEGER | Unique identifier for the generated article | Primary key, auto-incrementing |
| `title` | TEXT | Generated article title | Not null |
| `content` | TEXT | Generated article content | - |
| `category` | TEXT | Content category (e.g., "technology") | - |
| `source_articles` | TEXT | JSON array of source article IDs | Stored as JSON string |
| `generated_date` | TEXT | Generation timestamp (ISO format) | - |
| `status` | TEXT | Approval status ("pending", "approved", "rejected") | Default: "pending" |
| `feedback` | TEXT | User feedback if rejected | - |
| `edited_content` | TEXT | User-edited version (if any) | - |

#### 3.1.3 Indexes

- **Primary Key Index**: On `id` (automatically created)
- **Performance Index**: On `status` for filtering pending/approved content
- **Performance Index**: On `generated_date` for date-based filtering

#### 3.1.4 Example Data

```
id | title                         | content                   | category    | source_articles    | generated_date       | status   | feedback                  | edited_content
---|-------------------------------|---------------------------|-------------|--------------------|--------------------- |----------|---------------------------|---------------
1  | The Future of AI in Healthcare | <article content>        | technology  | [1, 3, 5]          | 2023-08-02T10:30:45Z | approved | null                      | null
2  | Quantum Computing Advances    | <article content>         | technology  | [2, 7, 9]          | 2023-08-02T10:45:20Z | rejected | Needs more technical info | null
```

### 3.2 Table: `social_posts`

This table stores social media posts generated from articles.

#### 3.2.1 Schema Definition

```sql
CREATE TABLE social_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER,
    platform TEXT,
    content TEXT,
    generated_date TEXT,
    status TEXT DEFAULT 'pending',
    feedback TEXT,
    edited_content TEXT,
    FOREIGN KEY (article_id) REFERENCES generated_articles(id)
);

CREATE INDEX idx_article_id ON social_posts(article_id);
```

#### 3.2.2 Field Descriptions

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | INTEGER | Unique identifier for the social post | Primary key, auto-incrementing |
| `article_id` | INTEGER | ID of the related generated article | Foreign key to `generated_articles.id` |
| `platform` | TEXT | Social media platform (e.g., "twitter", "linkedin") | - |
| `content` | TEXT | Post content | - |
| `generated_date` | TEXT | Generation timestamp (ISO format) | - |
| `status` | TEXT | Approval status ("pending", "approved", "rejected") | Default: "pending" |
| `feedback` | TEXT | User feedback if rejected | - |
| `edited_content` | TEXT | User-edited version (if any) | - |

#### 3.2.3 Indexes

- **Primary Key Index**: On `id` (automatically created)
- **Foreign Key Index**: On `article_id` for relational queries

#### 3.2.4 Example Data

```
id | article_id | platform  | content                          | generated_date       | status   | feedback | edited_content
---|------------|-----------|----------------------------------|----------------------|----------|----------|---------------
1  | 1          | twitter   | New research shows AI can help... | 2023-08-02T10:35:15Z | approved | null     | null
2  | 1          | linkedin  | #Healthcare #AI: Our latest...    | 2023-08-02T10:35:30Z | pending  | null     | null
```

### 3.3 Common Queries

#### 3.3.1 Get Pending Content for Review

```sql
SELECT id, title, category, generated_date 
FROM generated_articles 
WHERE status = 'pending' 
ORDER BY generated_date ASC;
```

#### 3.3.2 Get Social Posts for an Article

```sql
SELECT id, platform, content, status 
FROM social_posts 
WHERE article_id = ? 
ORDER BY platform;
```

#### 3.3.3 Update Content Status

```sql
UPDATE generated_articles 
SET status = ?, feedback = ? 
WHERE id = ?;
```

## 4. Database Relationships

### 4.1 Entity-Relationship Diagram

```
┌───────────────┐        ┌───────────────────┐        ┌───────────────┐
│               │        │                   │        │               │
│    articles   │───────▶│  generated_articles │───────▶│  social_posts │
│    (News DB)  │        │   (Content DB)    │        │  (Content DB) │
│               │        │                   │        │               │
└───────────────┘        └───────────────────┘        └───────────────┘
```

### 4.2 Relationship Descriptions

1. **Articles to Generated Articles**: Many-to-many relationship
   - Multiple scraped articles can be used to generate a single AI article
   - The `source_articles` field in `generated_articles` stores the IDs of related articles

2. **Generated Articles to Social Posts**: One-to-many relationship
   - One generated article can have multiple social media posts
   - The `article_id` field in `social_posts` references the parent article

## 5. Data Management

### 5.1 Data Lifecycle

1. **Article Collection**:
   - News articles are scraped from sources
   - Articles are stored in the News Database

2. **Content Generation**:
   - AI generates content based on scraped articles
   - Generated content is stored in the Content Database with "pending" status

3. **Content Review**:
   - Users review, approve, reject, or edit content
   - Content status is updated accordingly

4. **Content Publishing**:
   - Approved content is available for publishing
   - Publishing status can be tracked in additional fields if needed

### 5.2 Data Retention

1. **News Database**:
   - Articles are retained indefinitely by default
   - Consider implementing an archiving strategy for older articles

2. **Content Database**:
   - Generated content is retained indefinitely by default
   - Consider implementing cleanup for rejected content after a certain period

### 5.3 Data Backup

1. **Backup Strategy**:
   - Regular backups of SQLite database files
   - Consider using SQLite's Online Backup API for consistent backups

2. **Backup Commands**:
   ```bash
   # Simple file copy backup
   cp data/news_database.db data/backups/news_database_$(date +%Y%m%d).db
   cp data/content_database.db data/backups/content_database_$(date +%Y%m%d).db
   
   # Using SQLite's .backup command
   sqlite3 data/news_database.db ".backup data/backups/news_database_$(date +%Y%m%d).db"
   sqlite3 data/content_database.db ".backup data/backups/content_database_$(date +%Y%m%d).db"
   ```

## 6. Database Extension Guide

### 6.1 Adding New Tables

When adding new functionality that requires additional data storage, follow these steps:

1. **Define Schema**:
   ```sql
   CREATE TABLE new_table (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       field1 TEXT NOT NULL,
       field2 INTEGER,
       ...
   );
   
   CREATE INDEX idx_field1 ON new_table(field1);
   ```

2. **Add Database Creation Code**:
   ```python
   def init_database(self):
       with sqlite3.connect(self.db_path) as conn:
           cursor = conn.cursor()
           cursor.execute('''
               CREATE TABLE IF NOT EXISTS new_table (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   field1 TEXT NOT NULL,
                   field2 INTEGER,
                   ...
               )
           ''')
           cursor.execute('''
               CREATE INDEX IF NOT EXISTS idx_field1 ON new_table(field1)
           ''')
   ```

3. **Add Data Access Methods**:
   ```python
   def save_new_data(self, data):
       with sqlite3.connect(self.db_path) as conn:
           cursor = conn.cursor()
           cursor.execute('''
               INSERT INTO new_table (field1, field2)
               VALUES (?, ?)
           ''', (data['field1'], data['field2']))
           return cursor.lastrowid
   
   def get_new_data(self, criteria):
       with sqlite3.connect(self.db_path) as conn:
           conn.row_factory = sqlite3.Row
           cursor = conn.cursor()
           cursor.execute('''
               SELECT * FROM new_table
               WHERE field1 = ?
           ''', (criteria,))
           return [dict(row) for row in cursor.fetchall()]
   ```

### 6.2 Modifying Existing Tables

When modifying existing tables, use SQLite's ALTER TABLE command:

```sql
-- Add a new column
ALTER TABLE articles ADD COLUMN new_field TEXT;

-- Add a new index
CREATE INDEX idx_new_field ON articles(new_field);
```

In Python:
```python
def migrate_database(self):
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(articles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'new_field' not in columns:
            cursor.execute('ALTER TABLE articles ADD COLUMN new_field TEXT')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_new_field ON articles(new_field)')
```

### 6.3 Database Migration Strategy

For more complex schema changes, follow this migration strategy:

1. **Version Database Schema**:
   ```python
   def get_schema_version(self):
       with sqlite3.connect(self.db_path) as conn:
           cursor = conn.cursor()
           cursor.execute('''
               CREATE TABLE IF NOT EXISTS schema_version (
                   version INTEGER PRIMARY KEY
               )
           ''')
           cursor.execute('SELECT version FROM schema_version')
           result = cursor.fetchone()
           return result[0] if result else 0
   
   def set_schema_version(self, version):
       with sqlite3.connect(self.db_path) as conn:
           cursor = conn.cursor()
           cursor.execute('DELETE FROM schema_version')
           cursor.execute('INSERT INTO schema_version VALUES (?)', (version,))
   ```

2. **Implement Migration Functions**:
   ```python
   def migrate_schema(self):
       current_version = self.get_schema_version()
       
       if current_version < 1:
           self._migrate_v0_to_v1()
           current_version = 1
       
       if current_version < 2:
           self._migrate_v1_to_v2()
           current_version = 2
       
       # Set final version
       self.set_schema_version(current_version)
   
   def _migrate_v0_to_v1(self):
       with sqlite3.connect(self.db_path) as conn:
           cursor = conn.cursor()
           # Migration code...
   
   def _migrate_v1_to_v2(self):
       with sqlite3.connect(self.db_path) as conn:
           cursor = conn.cursor()
           # Migration code...
   ```

## 7. JSON Data Handling

Several fields in the database store complex data as JSON strings. Here's how to work with them:

### 7.1 Storing JSON Data

```python
import json

def save_article(self, article_data):
    # Convert keywords list to JSON string
    keywords_json = json.dumps(article_data['keywords'])
    
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO articles (title, content, url, keywords)
            VALUES (?, ?, ?, ?)
        ''', (
            article_data['title'],
            article_data['content'],
            article_data['url'],
            keywords_json
        ))
```

### 7.2 Retrieving JSON Data

```python
def get_article(self, article_id):
    with sqlite3.connect(self.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()
        
        if row:
            article = dict(row)
            # Parse JSON string back to Python object
            article['keywords'] = json.loads(article['keywords']) if article['keywords'] else []
            return article
        return None
```

## 8. Performance Considerations

### 8.1 Query Optimization

1. **Use Indexes**: Ensure appropriate indexes for frequent query patterns
2. **Limit Results**: Use LIMIT clauses for large result sets
3. **Select Specific Columns**: Only retrieve needed columns

### 8.2 Transaction Management

1. **Batch Operations**: Use transactions for multiple operations
   ```python
   with sqlite3.connect(self.db_path) as conn:
       cursor = conn.cursor()
       try:
           # Begin transaction
           cursor.execute('BEGIN TRANSACTION')
           
           # Multiple operations
           for article in articles:
               cursor.execute('INSERT INTO articles VALUES (?, ?, ?)', 
                             (article['title'], article['content'], article['url']))
           
           # Commit transaction
           cursor.execute('COMMIT')
       except Exception as e:
           # Rollback on error
           cursor.execute('ROLLBACK')
           raise e
   ```

2. **Connection Pooling**: For high-concurrency scenarios, consider implementing connection pooling

### 8.3 Database Maintenance

Periodic maintenance can help maintain performance:

```python
def optimize_database(self):
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('VACUUM')
        cursor.execute('ANALYZE')
```

## 9. Conclusion

This database schema documentation provides a comprehensive guide to the data storage components of the Agentic News Workflow System. By understanding these schemas, developers can effectively query, modify, and extend the system's data storage capabilities to meet evolving requirements.

For further assistance with database operations or schema modifications, consult the SQL documentation or reach out to the development team.
