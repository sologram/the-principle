import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel


# =========================
# 选择模型
# =========================

MODEL = "bert-base-chinese"
# 也可以:
# "Qwen/Qwen2.5-7B"
# "BAAI/bge-large-zh-v1.5"
# "hfl/chinese-roberta-wwm-ext"


device = "cuda" if torch.cuda.is_available() else "cpu"


tokenizer = AutoTokenizer.from_pretrained(
    MODEL,
    trust_remote_code=True
)

model = AutoModel.from_pretrained(
    MODEL,
    output_hidden_states=True,
    trust_remote_code=True
).to(device)

model.eval()



# =========================
# 获取 hidden vector
# =========================

def get_vector(text, layer=-1):

    inputs = tokenizer(
        text,
        return_tensors="pt"
    ).to(device)


    with torch.no_grad():

        outputs = model(**inputs)


    # hidden_states:
    # layer 0 = embedding
    # layer -1 = 最后一层

    h = outputs.hidden_states[layer]


    # mean pooling
    mask = inputs["attention_mask"]

    mask = mask.unsqueeze(-1)

    vec = (
        h * mask
    ).sum(dim=1) / mask.sum(dim=1)


    return vec[0]



# =========================
# 方向
# =========================

def concept_axis(pos, neg):

    p = get_vector(pos)
    n = get_vector(neg)

    return p - n



# =========================
# cosine
# =========================

def cosine(a,b):

    return F.cosine_similarity(
        a.unsqueeze(0),
        b.unsqueeze(0)
    ).item()



# =========================
# 构造概念轴
# =========================


axes = {

    "价值轴 好-坏":
        concept_axis(
            "好",
            "坏"
        ),


    "善恶轴 善-恶":
        concept_axis(
            "善",
            "恶"
        ),


    "合作轴 合作-冲突":
        concept_axis(
            "合作",
            "冲突"
        ),


    "真实轴 对-错":
        concept_axis(
            "正确",
            "错误"
        ),


    "效率轴 高效-低效":
        concept_axis(
            "高效",
            "低效"
        )
}



# =========================
# 比较概念方向
# =========================


pairs = [
    ("价值轴 好-坏", "合作轴 合作-冲突"),
    ("价值轴 好-坏", "善恶轴 善-恶"),
    ("价值轴 好-坏", "真实轴 对-错"),
    ("价值轴 好-坏", "效率轴 高效-低效"),
]


print("\n=== Concept direction similarity ===")

for a,b in pairs:

    print(
        a,
        "<->",
        b,
        cosine(
            axes[a],
            axes[b]
        )
    )



# =========================
# 找靠近好的一组词
# =========================


good_axis = axes["价值轴 好-坏"]


words = [

    "合作",
    "信任",
    "帮助",
    "创造",
    "善良",
    "效率",
    "财富",
    "力量",

    "欺骗",
    "破坏",
    "冲突",
    "伤害",
    "战争"

]


print("\n=== Projection on GOOD axis ===")


for w in words:

    v = get_vector(w)

    score = cosine(
        v,
        good_axis
    )

    print(
        f"{w:6s}",
        score
    )
