def puanla_bina_yasi(yas):
    if yas is None:
        return 1  # varsayılabilir risk
    return (
        0 if yas <= 10 else
        1 if yas <= 25 else
        2 if yas <= 40 else
        3
    )

def puanla_kat_sayisi(kat):
    if kat is None:
        return 1
    return (
        0 if kat <= 2 else
        1 if kat <= 5 else
        2 if kat <= 9 else
        3
    )

def puanla_tasiyici_sistem(sistem):
    puan_tablosu = {
        1: 0,  # Betonarme çerçeve
        2: 1,  # Betonarme karma
        3: 2,  # Yığma
        4: 3,  # Ahşap
        5: 3   # Belirsiz
    }
    return puan_tablosu.get(sistem, 3)

def puanla_yapi_kayit_belgesi(belge):
    return 2 if belge and belge.strip() else 0

def puanla_yukseklik(yukseklik):
    if yukseklik is None:
        return 1
    return (
        0 if yukseklik <= 6 else
        1 if yukseklik <= 15 else
        2 if yukseklik <= 25 else
        3
    )

def puanla_tespit_aciklama(aciklama):
    if not aciklama or not isinstance(aciklama, str):
        return 0
    riskli_kelime = any(k in aciklama.lower() for k in ["risk", "güçlendirme", "yıkım"])
    return 3 if riskli_kelime else 0

def hesapla_deprem_riski(row):
    puan = 0
    puan += puanla_bina_yasi(row.get("BINAYASI"))
    puan += puanla_kat_sayisi(row.get("ZEMINUSTUKATSAYISI"))
    puan += puanla_tasiyici_sistem(row.get("TASIYICISISTEM"))
    puan += puanla_yapi_kayit_belgesi(row.get("YAPIKAYITBELGENO"))
    puan += puanla_yukseklik(row.get("TOPLAMYUKSEKLIK"))
    puan += puanla_tespit_aciklama(row.get("TESPITKARARACIKLAMA"))

    # Sonuç aralığını belirle
    if puan <= 3:
        return 1  # Çok Düşük Risk
    elif puan <= 6:
        return 2  # Düşük Risk
    elif puan <= 9:
        return 3  # Orta Risk
    elif puan <= 12:
        return 4  # Yüksek Risk
    else:
        return 5  # Çok Yüksek Risk
