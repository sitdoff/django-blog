import redis

redis_db = 1


def increase_post_views(post: "Post") -> None:
    """
    Increases the number of views by 1.
    If there are no views yet, it creates a key for the post and sets the value to 1.
    """
    key = f"{post._meta.model_name}:{post.pk}:views"
    with redis.Redis(host="redis", port=6379, db=redis_db) as redis_connect:
        redis_connect.hincrby("post_views", key, 1)


def get_post_views(post: "Post") -> str:
    """
    Returns the number of views for a post.
    """
    key = f"{post._meta.model_name}:{post.pk}:views"
    with redis.Redis(host="redis", port=6379, db=redis_db) as redis_connect:
        views: bytes = redis_connect.hget("post_views", key)
    return views.decode() if views is not None else "0"
