from fastmcp import FastMCP
import feedparser

mcp = FastMCP(name = "FreecodeCamp feed searcher")

@mcp.tool()
def fcc_new_search(query: str, max_results: int = 5):
    """Searches FreecodeCamp news feed via RSS by title and description."""
    feed_url = "https://www.freecodecamp.org/news/rss/"
    feed = feedparser.parse(feed_url)
    results = []
    query_lower = query.lower()
    for entry in feed.entries:
        title = entry.get("title", "")
        description = entry.get("description", "")
        if query_lower in title.lower() or query_lower in description.lower():
            results.append({
                "title": title,
                "url": entry.get("link", ""),
            })
        if len(results) >= max_results:
            break
    return results or ("No results found.",
                       "Try different keywords or increase max_results."
                       )
@mcp.tool()
def fcc_youtube_search(query: str, max_results: int = 5):
    """Searches FreecodeCamp news feed via RSS for YouTube links."""
    feed_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UC8butISFwT-Wl7EV0hUK0BQ"
    feed = feedparser.parse(feed_url)
    results = []
    query_lower = query.lower()
    for entry in feed.entries:
        title = entry.get("title", "")
        if (query_lower in title.lower()):
            results.append({
                "title": title,
                "url":entry.get("link", ""),
            })
        if len(results) >= max_results:
            break
    return results or ("No YouTube results found.")
@mcp.tool()
def fcc_secret_message():
    """Returns a secret message."""
    return "Congratulations! You've found the secret message hidden in the FreecodeCamp feed searcher MCP."

if __name__ == "__main__":
    mcp.run()
