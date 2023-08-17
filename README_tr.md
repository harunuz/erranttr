[[EN]](/)**[TR]**

# ERRANT-TR
[Towards Automatic Grammatical Error Type Classification for Turkish](https://aclanthology.org/2023.eacl-srw.14/)
yayını için resmi repo.


Doğal dil işleme başlıklarından dil bilgisi hatalarını düzeltme (Grammatical Error Correction) alanında otomatik 
değerlendime aracı olarak kullanılan [ERRANT](https://www.aclweb.org/anthology/P17-1074/) 'ın Türkçe için düzenlenmiş
versiyonu.

Bu kod ERRANT'ın [resmi reposunun](https://github.com/chrisjbryant/errant) üzerine kurulmuştur. 
Çalışma prensibi ve kod tasarımı aynıdır. Kullanım ve anahtar kelimeler hakkında detaylı bilgi için o repoya göz
gezdirebilirsiniz.

### Bağlılıklar
- [zemberek-python](https://github.com/loodos/zemberek-python)
- [rapidfuzz](https://github.com/maxbachmann/RapidFuzz)

Kullanmadan önce [erranttr/tr/resources](erranttr/tr/resources) dizinine,
sağda 0.1.0 versiyonunun eklerinde bulunan şu dosyaları indirmelisiniz:
1. **tr_TR.aff** ([hunspell-tr](https://github.com/tdd-ai/hunspell-tr) çalışmasından alınmıştır)
2. **TS_Corpus_Turkish_Word_List.zip** ([tdd](https://data.tdd.ai/#/16e5fbcf-a658-424d-b50c-4454a4b367dc) Türkçe veri kaynağı platformundan alınmıştır.)

Zip dosyasını çıkarmanız gerekmektedir.

## Veri Kümesi

Veri kümesi çeşitli akademik yayınlardan toplanan 106 doğru-hatalı cümle ikililerinden (paralel veri) oluşmaktadır. 
Etiketleme bir dil bilimci tarafından orijinalinden daha geniş bir hata tipleri ile yapılmıştır. 
ERRANT'ın kullandığı hata tiplerini kullanmak için Türkçe'ye özel eklenen hata tiplerini ERRANT'ın bazı hata kodlarına 
eşlemek gerekmektedir. Veri hakkında detaylı bilgi için yayının 4.1'inci bölümüne göz gezdirebilirsiniz.

Cümle ikilileri, M2 formatında etiketlenmiş veri, M2 formatında eşlenmiş hata tipleriyle etiketlenmiş veri, ve 
ERRANT-TR'nin cümle ikilileri için ürettiği tahminler [erranttr/tr/resources](erranttr/tr/resources) dizininde 
bulunmaktadır. 

### Çalışmanın Tekrarlanabilirliği
Koddaki bazı hata türlerini (özellikle NOUN:POSS ve SPELL'i) etkileyen küçük bir hata giderildi. Bu sebeple doğruluk
değerleri yayında paylaşılan değerlerin aynısı değildir; ancak oldukça yakındır. 
Bu versiyon hedeflendiği şekilde çalışmaktadır. Dolayısıyla lütfen bu versiyonu kullanınız. 
[predictions_W_MAPPED_LABELS_IN_PAPER.txt](erranttr/tr/resources/predictions_W_MAPPED_LABELS_IN_PAPER.txt)
dosyasında yayın tarihindeki versiyonla üretilmiş çıktıları bulabilirsiniz.

### Hata Tipi Eşleme
ERRANT-TR ERRANT'tan daha geniş bir hata kümesinde çalışmaktadır. Karar mekanizmasını geliştirirken o hata türlerinden
daha fazlasını (genellikle Türkçe'ye özel olanları) yakalayabildiğimizi farkettik ve ileride geliştirilecek çalışmalar 
için bu hata türlerine de destek verdik. ERRANT ile anlamlı bir karşılaştırma yapabilmek amacıyla bu hata türlerini
en yakın ERRANT türüne eşlemekteyiz. Hangi hataların eşlendiği ve basit örnekler aşağıda verilmiştir.

| Yeni Etiket         | ERRANT Eşleniği | Örnek                                    |
|---------------------|-----------------|------------------------------------------|
| DA                  | SPELL           | cay ictim -> çay içtim                   |
| ACCENT              | SPELL           | geliyom -> geliyorum                     |
| NOUN:CASE           | NOUN:INFL       | evde gidiyorum -> eve gidiyorum          |
| NOUN:NUM:SURF       | NOUN:INFL       | saatlar -> saatler                       |
| ADJ:CASE            | ADJ             | korkaklar sevmem -> korkakları sevmem    |
| VERB:INFL:TENSE     | VERB:TENSE      | dün geliyorum -> dün gelmiştim           |
| NOUN:PHRASE         | OTHER           | kitabının kapağı -> kitabın kapağı       |
| NOUN:STC:NEG        | VERB            | bende kalem değil -> bende kalem yok     |
| NOUN-VERB:INFL:CASE | NOUN:INFL       | gelme düşünüyorum -> gelmeyi düşünüyorum |
| PRON:CASE           | NOUN:INFL       | o söyledim -> ona söyledim               |
| PRON:INFL           | NOUN:INFL       | odan aldım -> ondan aldım                |
| PRON:POSS           | NOUN:POSS       | onu kalemi -> onun kalemi                |


### Kullanım

erranttr package dizinine gidiniz. (erranttr/erranttr)
```
cd /path/to/erranttr/erranttr
```

Paralel veriyi işleyip M2 formatında kaydetmek için process.py script'i çalıştırılmalıdır. Bu script
[sentences.txt](erranttr/tr/resources/sentences.txt) dosyasını okur, girdi olarak aldığı çıktı dosya ismine
tahminleri kaydeder.

```
python process.py predictions.txt
```

ERRANT-TR'ye özel hata tiplerini ERRANT eşleniklerine dönüştürmek için map_labels.py script'ini çalıştırın.

```
python map_labels.py predictions.txt
```
Değerlendirme verisi ile tahminleri karşılaştırmak için compare_m2.py script'ini çalıştırın.

```
python commands/compare_m2.py -hyp "output/predictions_W_MAPPED_LABELS.txt" -ref tr/resources/eval_data_W_MAPPED_LABELS.txt -b 0.5 -cse -cat 2
```
