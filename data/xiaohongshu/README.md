# Xiaohongshu extraction records

`posts.jsonl` stores one JSON object per post. Use the stable 24-character post ID
from the post URL as `post_id`. `records.py` computes `hash_id` as SHA-256 of
the UTF-8 string `xiaohongshu:<post_id>`. The hash identifies a post, not a
particular revision of its content. Do not save temporary access tokens in URLs.

Only mark a post `complete` after all requested material has been reviewed;
otherwise use `partial` and explain what remains. Store only material actually
observed, and distinguish any transcriptions or descriptions from assumptions.
Suggested optional fields include `source_url`, `title`, `author`, `text`,
`images`, `notes`, and `observed_at`. The script merges fields on upsert, so
include revised values when updating them.

In PowerShell, upsert one record from JSON. Set UTF-8 for the pipe so Chinese
text is preserved; `-X utf8` tells Python to read and write UTF-8:

```powershell
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
@{ post_id = '0123456789abcdef01234567'; status = 'partial'; notes = 'Example only' } |
  ConvertTo-Json -Depth 10 -Compress | python -X utf8 data/xiaohongshu/records.py upsert
```

List IDs to skip on the next extraction, and IDs that still need attention:

```powershell
python data/xiaohongshu/records.py list --status complete
python data/xiaohongshu/records.py list --status partial
```

Validate the store and its hashes:

```powershell
python data/xiaohongshu/records.py validate
```

The store is local to this workspace. A missing `posts.jsonl` is an empty store;
the first upsert creates it. The script uses only Python's standard library.
