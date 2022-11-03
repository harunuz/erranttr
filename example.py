import erranttr

annotator = erranttr.load('tr')

# m = TurkishMorphology.create_with_defaults()

origs = [
    "Günümüzde pek çok hastalıkla yaşamaya devam ederiz.",
    "Sağlığımizi korumak için ne yapmaliyiz."
]

corrs = [
    "Günümüzde çok hastaliklerle yaşamaya devam ediyoruz.",
    "Sağlığımızı korumak için ne yapmalıyız?"
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
