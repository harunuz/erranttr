import erranttr

annotator = erranttr.load('tr')

# m = TurkishMorphology.create_with_defaults()

origs = [
    # "Ne yani dişarı çikabilirmiyiz?",
    # "Halbuki ben çok sevmişdim onu",
    # "Bence dünyada salgın hastalıkların oldumağı yer mümkündür.",
    # "Günümüzde çok hastaliklerle yaşamaya devam ediyoruz.",
    # "Sağlığımizi korumak için ne yapmaliyiz.",
    "Sonunda yabancı bir ülkelere yasmak için gitseydik, olumlu ve olumsuz hayatın özellikleri gözlerimizin önünde koymalıyız."
]

corrs = [
    # "Ne yani dışarı çıkabilir miyiz?",
    # "Halbuki ben çok sevmiştim onu",
    # "Bence dünyada salgın hastalıkların olmadığı yer mümkündür.",
    # "Günümüzde pek çok hastalıkla yaşamaya devam ederiz.",
    # "Sağlığımızı korumak için ne yapmalıyız?",
    "Sonunda yabancı bir ülkeye yaşamak için gitseydik, olumlu ve olumsuz hayatın özelliklerini gözlerimizin önüne koymalıyız."
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
