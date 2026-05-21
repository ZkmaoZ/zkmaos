from storage import vectors


def test_embed_normalized():
    v = vectors.embed("hello world hello")
    norm_sq = sum(x * x for x in v.values())
    assert abs(norm_sq - 1.0) < 1e-9


def test_cosine_self_is_one():
    v = vectors.embed("LLM agent evaluation benchmark")
    assert abs(vectors.cosine(v, v) - 1.0) < 1e-9


def test_cosine_disjoint_zero():
    a = vectors.embed("apple banana cherry")
    b = vectors.embed("동해물과 백두산이")
    assert vectors.cosine(a, b) == 0.0


def test_query_ranks_by_similarity():
    vectors.init()
    vectors.upsert("d1", "u1", "LLM agent benchmark", "evaluation harness LLM agents")
    vectors.upsert("d2", "u2", "비빔밥 레시피", "고추장 참기름 나물")
    hits = vectors.query("LLM evaluation", top_k=2)
    assert hits and hits[0].doc_id == "d1"
    assert hits[0].score > (hits[1].score if len(hits) > 1 else 0)
