#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gera CSVs para popular o esquema:
tb_address, tb_card, tb_role, tb_congresso, tb_user, tb_user_role,
tb_article, tb_articles_users, tb_evaluation, tb_review

Alvo: ~1 GB total (ajuste fino em ARTICLE_BODY_KB).
Cria arquivos em ./out
"""

import os
import csv
import random
import uuid
from pathlib import Path
from datetime import datetime, timedelta

# =============== CONFIGURAÇÃO (ajuste fino aqui) ===============
OUT_DIR = Path("./out")

# Quantidades pensadas para ~1 GB total
N_USERS       = 900_000
N_CONGRESSOS  = 100_00
N_ARTICLES    = 800_000

# Relações auxiliares
REVIEWS_PER_ARTICLE          = 2     # número médio fixo por artigo
ARTICLES_USERS_PER_ARTICLE   = 2     # autores por artigo (muitos-para-muitos)
EVALUATION_RATIO             = 0.70  # % de artigos com evaluation

# Tamanho médio do corpo do artigo em KB (aceita decimal)
# 150k * ~6.21 KB ≈ 0.89–0.95 GB (o restante completa ~1 GB)
ARTICLE_BODY_KB = 6.21 * 5   
# ================================================================

random.seed(42)

FIRST_NAMES = [
    "Ana","Carlos","Mariana","Felipe","João","Beatriz","Lucas","Julia",
    "Pedro","Larissa","Paulo","Rafaela","Renata","Miguel","Sofia","Mateus",
    "Isabela","Gustavo","Camila","André"
]
LAST_NAMES  = [
    "Silva","Souza","Oliveira","Santos","Pereira","Costa","Rocha","Almeida",
    "Ribeiro","Gomes","Carvalho","Araújo","Lima","Barbosa","Castro","Teixeira"
]
CITIES  = ["São Paulo","Salvador","Rio de Janeiro","Fortaleza","Curitiba",
           "Manaus","Recife","Belo Horizonte","Porto Alegre","Florianópolis","Vitória"]
STATES  = ["SP","BA","RJ","CE","PR","AM","PE","MG","RS","SC","ES"]
COUNTRY = "Brasil"
STREETS = ["Rua das Flores","Av. Central","Rua Bahia","Rua da Paz","Av. Atlântica",
           "Rua Projetada","Av. Brasil","Rua Sete","Rua das Palmeiras"]

WORK_PLACES = ["USP","UFBA","UFRJ","Hospital Municipal","Clínica Central",
               "UESC","Laboratório Next","SUSConecta Org","IFBA","Unicamp"]

AUTHORITIES = ["ROLE_USER","ROLE_REVIEWER","ROLE_ADMIN"]
ARTICLE_STATUS = ["PENDING","VALID","EXPIRED"]
CONGRESS_MODALITY = ["ONLINE","IN_PERSON","HYBRID"]

def ensure_outdir():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

def write_csv(path: Path, header, rows_iter):
    with open(path, "w", newline='', encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for i, row in enumerate(rows_iter, 1):
            w.writerow(row)
            if i % 100_000 == 0:
                print(f"[{path.name}] {i:,} linhas geradas")

def rand_dt_between(days_back=3650):
    now = datetime.utcnow()
    return now - timedelta(days=random.randint(0, days_back),
                           seconds=random.randint(0, 86400))

def make_article_body(kb: float = 6.0) -> str:
    """
    Gera ~kb*1024 bytes de texto (aprox), repetindo um chunk.
    Obs.: texto repetitivo comprime um pouco. Se quiser menos compressível,
    troque por bytes pseudoaleatórios e encode em base64.
    """
    target_bytes = int(kb * 1024)
    chunk = ("lorem ipsum dolor sit amet consectetur adipiscing elit "
             "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ")
    s = []
    size = 0
    while size < target_bytes:
        s.append(chunk)
        size += len(chunk)
    txt = "".join(s)
    return txt[:target_bytes]

# ====================== GERADORES DE DADOS ======================

def gen_addresses(n):
    for i in range(1, n+1):
        city = random.choice(CITIES)
        st   = random.choice(STATES)
        yield [
            i,
            city,
            f"Comp {i%100}",
            COUNTRY,
            str(random.randint(1,9999)),
            st,
            random.choice(STREETS),
            f"{random.randint(10000,99999)}-{random.randint(100,999)}"
        ]

def gen_cards(n):
    for i in range(1, n+1):
        cvv = random.randint(100, 999)
        expired = (datetime.utcnow() + timedelta(days=random.randint(30, 365*5))).date().isoformat()
        number = f"{random.randint(4000,4999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        yield [i, cvv, expired, number]

def gen_roles():
    for i, auth in enumerate(AUTHORITIES, start=1):
        yield [i, auth]

def gen_congressos(n):
    for i in range(1, n+1):
        minr = random.randint(2,3)
        maxr = random.randint(4,6)
        start = rand_dt_between(3650)
        end   = start + timedelta(days=random.randint(2,5))
        review_deadline = end + timedelta(days=random.randint(5,20))
        submission_deadline = start - timedelta(days=random.randint(10,60))
        modality = random.choice(CONGRESS_MODALITY)
        desc = f"Congresso {i} sobre IA e Medicina"
        desc_title = f"Congresso {i}"
        # image_thumbnail -> vazio (NULL/empty) para simplificar
        place = random.choice(CITIES)
        name = f"CG-{i:04d}"
        yield [
            i,                      # id
            maxr,                   # max_reviews_per_article
            minr,                   # min_reviews_per_article
            end.isoformat(sep=' '), # end_date
            review_deadline.isoformat(sep=' '),
            start.isoformat(sep=' '),
            submission_deadline.isoformat(sep=' '),
            modality,
            desc,
            desc_title,
            "",                     # image_thumbnail
            name,
            place
        ]

def gen_users(n, max_congresso_id):
    # address_id e card_id 1:1 com user_id (garante UNIQUE sem colisão)
    for i in range(1, n+1):
        fname = random.choice(FIRST_NAMES); lname = random.choice(LAST_NAMES)
        username = f"{fname.lower()}.{lname.lower()}.{i}"
        login = username
        pwd = "hashed_pwd"  # placeholder
        is_reviewer = random.random() < 0.35
        membership = str(uuid.uuid4())
        work_place = random.choice(WORK_PLACES)
        congresso_id = random.randint(1, max_congresso_id) if max_congresso_id>0 and random.random()<0.3 else ""
        yield [
            i,                 # id
            is_reviewer,       # is_reviewer
            i,                 # address_id
            i,                 # card_id
            congresso_id,      # congresso_id (pode ser vazio)
            membership,
            login,
            pwd,
            f"{fname} {lname}",# username_user
            work_place,
            ""                 # profile_image
        ]

def gen_user_roles(n_users):
    # 1=USER, 2=REVIEWER, 3=ADMIN
    for u in range(1, n_users+1):
        yield [1, u]
        if random.random() < 0.35:
            yield [2, u]
        if random.random() < 0.02:
            yield [3, u]

def gen_articles(n, max_congresso_id):
    for i in range(1, n+1):
        status = random.choice(ARTICLE_STATUS)
        title = f"Article {i}: Advances in AI"
        description = f"Resumo do artigo {i}"
        published_at = rand_dt_between(3650).isoformat(sep=' ')
        congresso_id = random.randint(1, max_congresso_id) if max_congresso_id>0 else ""
        body = make_article_body(ARTICLE_BODY_KB)
        yield [
            i, congresso_id, published_at, description, "PDF", status, title, body
        ]

def gen_articles_users(n_articles, n_users, authors_per_article):
    for a in range(1, n_articles+1):
        authors = random.sample(range(1, n_users+1), k=min(authors_per_article, n_users))
        for u in authors:
            yield [a, u]

def gen_evaluations(n_articles, ratio):
    total = int(n_articles * ratio)
    chosen = sorted(random.sample(range(1, n_articles+1), total))
    for idx, a in enumerate(chosen, start=1):
        final_score = round(random.uniform(0, 10), 2)
        n_reviews = random.randint(1, 8)
        yield [idx, final_score, n_reviews, a]

def gen_reviews(n_articles, reviews_per_article, n_users, max_eval_id):
    rid = 0
    for a in range(1, n_articles+1):
        k = int(reviews_per_article)
        for _ in range(k):
            rid += 1
            score = random.randint(0, 10)
            create_at = rand_dt_between(3650).isoformat(sep=' ')
            reviewer_id = random.randint(1, n_users)
            comment = f"Review {rid} do artigo {a}"
            evaluation_id = random.randint(1, max_eval_id) if max_eval_id>0 and random.random()<0.7 else ""
            yield [rid, score, a, create_at, evaluation_id, reviewer_id, comment]

# ============================ MAIN ==============================

def main():
    ensure_outdir()

    print(">> Gerando tb_address.csv ...")
    write_csv(
        OUT_DIR/"tb_address.csv",
        ["id","city","complement","country","number","state","street","zip_code"],
        gen_addresses(N_USERS)
    )

    print(">> Gerando tb_card.csv ...")
    write_csv(
        OUT_DIR/"tb_card.csv",
        ["id","cvv","expired","number"],
        gen_cards(N_USERS)
    )

    print(">> Gerando tb_role.csv ...")
    write_csv(
        OUT_DIR/"tb_role.csv",
        ["id","authority"],
        gen_roles()
    )

    print(">> Gerando tb_congresso.csv ...")
    # Ordem das colunas aqui deve bater com a lista usada no COPY:
    # (id,max_reviews_per_article,min_reviews_per_article,end_date,review_deadline,
    #  start_date,submission_deadline,congresso_modality,description,description_title,
    #  image_thumbnail,name,place)
    write_csv(
        OUT_DIR/"tb_congresso.csv",
        ["id","max_reviews_per_article","min_reviews_per_article","end_date","review_deadline",
         "start_date","submission_deadline","congresso_modality","description","description_title",
         "image_thumbnail","name","place"],
        gen_congressos(N_CONGRESSOS)
    )

    print(">> Gerando tb_user.csv ...")
    write_csv(
        OUT_DIR/"tb_user.csv",
        ["id","is_reviewer","address_id","card_id","congresso_id","membership_number",
         "login","password","username_user","work_place","profile_image"],
        gen_users(N_USERS, N_CONGRESSOS)
    )

    print(">> Gerando tb_user_role.csv ...")
    write_csv(
        OUT_DIR/"tb_user_role.csv",
        ["role_id","user_id"],
        gen_user_roles(N_USERS)
    )

    print(">> Gerando tb_article.csv ...")
    write_csv(
        OUT_DIR/"tb_article.csv",
        ["id","congresso_id","published_at","description","format","status","title","body"],
        gen_articles(N_ARTICLES, N_CONGRESSOS)
    )

    print(">> Gerando tb_articles_users.csv ...")
    write_csv(
        OUT_DIR/"tb_articles_users.csv",
        ["article_id","user_id"],
        gen_articles_users(N_ARTICLES, N_USERS, ARTICLES_USERS_PER_ARTICLE)
    )

    print(">> Gerando tb_evaluation.csv ...")
    eval_rows = list(gen_evaluations(N_ARTICLES, EVALUATION_RATIO))
    write_csv(
        OUT_DIR/"tb_evaluation.csv",
        ["id","final_score","number_of_reviews","article_id"],
        eval_rows
    )
    max_eval_id = len(eval_rows)

    print(">> Gerando tb_review.csv ...")
    write_csv(
        OUT_DIR/"tb_review.csv",
        ["id","score","article_id","create_at","evaluation_id","reviewer_id","comment"],
        gen_reviews(N_ARTICLES, REVIEWS_PER_ARTICLE, N_USERS, max_eval_id)
    )

    print("\n✔ CSVs gerados em ./out")
    print("   Ajuste ARTICLE_BODY_KB para calibrar o total (~1 GB).")

if __name__ == "__main__":
    main()
