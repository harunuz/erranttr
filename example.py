import erranttr

annotator = erranttr.load('tr')

# m = TurkishMorphology.create_with_defaults()

origs = [
    # "Ne yani dişarı çikabilirmiyiz?",
    # "Halbuki ben çok sevmişdim onu",
    # "Bence dünyada salgın hastalıkların oldumağı yer mümkündür.",
    # "Günümüzde çok hastaliklerle yaşamaya devam ediyoruz.",
    # "Sağlığımizi korumak için ne yapmaliyiz.",
    # "Sonunda yabancı bir ülkelere yasmak için gitseydik, olumlu ve olumsuz hayatın özellikleri gözlerimizin önünde koymalıyız.",
    # "Adam sabah ve geç uyandı",
    # "Geç kaldığı yüzden patronu kızdı",
    # "Ötöbüs gibi işe gidecekdi",
    # "Adam bir yere gitmek gibi koşuyor",
    # "Hafta sonu sinemaya gittik, film izlendi.",
    "Ötöbüs gibi işe gidecekdi",
    "Geç kaldığı yüzden patronu kızdı",
    "Zorluklar hayat baş ettmk öğrenir.",
    "Birinci resimde beyefendi sol eldeki saati göstermiş"
]

corrs = [
    # "Ne yani dışarı çıkabilir miyiz?",
    # "Halbuki ben çok sevmiştim onu",
    # "Bence dünyada salgın hastalıkların olmadığı yer mümkündür.",
    # "Günümüzde pek çok hastalıkla yaşamaya devam ederiz.",
    # "Sağlığımızı korumak için ne yapmalıyız?",
    # "Sonunda yabancı bir ülkeye yaşamak için gitseydik, olumlu ve olumsuz hayatın özelliklerini gözlerimizin önüne koymalıyız.",
    # "Adam sabah da geç uyandı",
    # "Geç kaldığı için patronu kızdı",
    # "Otobüs ile işe gidecekti",
    # "Adam bir yere gitmek için koşuyor",
    # "Hafta sonu sinemaya gittik, film izledik.",
    "Otobüs ile işe gidecekti",
    "Geç kaldığı için patronu kızdı",
    "Zorluklar hayatla baş etmeyi öğretir.",
    "Birinci resimde beyefendi sol elindeki saati göstermiş"
]

print("====================================================================================\n")
for s1, s2 in zip(origs, corrs):

    # ali = Alignment(s1, s2)

    # print(ali)

    orig = annotator.parse(s1)
    cor = annotator.parse(s2)

    edits = annotator.annotate(orig, cor)

    for e in edits:
        print(f"{e.o_start} {e.o_end} {e.o_str}\t\t{e.c_start} {e.c_end} {e.c_str}\t\t{e.type}")

    print("====================================================================================\n")
