import sys
sys.path.insert(0, "src")
from zephyr.vector_memory.embedding_router import EmbeddingRouter

router = EmbeddingRouter(backend="local")
router._load_bge_small()
print(f"bge-small available: {router.bge_small_available}")
print(f"bge-small dim: {router.bge_small_dim}")

if router.bge_small_available:
    vec = router._embed_bge_small("测试嵌入模型是否正常工作")
    print(f"嵌入成功! dim={vec.shape[0]}, norm={float(vec.dot(vec)):.4f}")

    vec2 = router._embed_bge_small("部署到生产环境")
    vec3 = router._embed_bge_small("deploy v2.3 to production")
    cos_sim = float(vec2.dot(vec3))
    print(f"语义相似度测试:")
    print(f"  '部署到生产环境' vs 'deploy v2.3 to production' = {cos_sim:.4f}")

    vec4 = router._embed_bge_small("今天天气真好")
    cos_diff = float(vec2.dot(vec4))
    print(f"  '部署到生产环境' vs '今天天气真好' = {cos_diff:.4f}")
    print(f"  相似句得分 > 无关句得分: {cos_sim > cos_diff}")
else:
    print("bge-small 加载失败!")