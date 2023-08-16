[[EN]](erranttr/)**[TR]**

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


## Veri Kümesi

Veri kümesi çeşitli akademik yayınlardan toplanan 106 doğru-hatalı cümle ikililerinden (paralel veri) oluşmaktadır. 
Etiketleme bir dil bilimci tarafından orijinalinden daha geniş bir hata tipleri ile yapılmıştır. 
ERRANT'ın kullandığı hata tiplerini kullanmak için Türkçe'ye özel eklenen hata tiplerini ERRANT'ın bazı hata kodlarına 
eşlemek gerekmektedir. Veri hakkında detaylı bilgi için yayının 4.1'inci bölümüne göz gezdirebilirsiniz.

Cümle ikilileri, M2 formatında etiketlenmiş veri, M2 formatında eşlenmiş hata tipleriyle etiketlenmiş veri, ve 
ERRANT-TR'nin cümle ikilileri için ürettiği tahminler [erranttr/tr/resources](erranttr/tr/resources) dizininde 
bulunmaktadır. 

### Kullanım

Paralel veriyi işleyip M2 formatında kaydetmek için process.py script'i çalıştırılmalıdır. Bu script
[sentences.txt](erranttr/tr/resources/sentences.txt) dosyasını okur, girdi olarak aldığı çıktı dosya ismine
tahminleri kaydeder.

`python erranttr/erranttr/process.py predictions.txt`

ERRANT-TR'ye özel hata tiplerini ERRANT eşleniklerine dönüştürmek için map_labels.py script'ini çalıştırın.

`python erranttr/erranttr/map_labels.py predictions.txt`

Değerlendirme verisi ile tahminleri karşılaştırmak için compare_m2.py script'ini çalıştırın.

```
python erranttr/erranttr/commands/compare_m2.py -hyp erranttr/erranttr/tr/resources/eval_data_preds_W_MAPPED_LABELS_0.txt -ref erranttr/erranttr/tr/resources/eval_data_W_MAPPED_LABELS_0.txt -b 0.5 -cse -cat 2
```

### Not
Kullanmadan önce [erranttr/tr/resources](erranttr/tr/resources) dizinine,
sağda 0.1.0 versiyonunun eklerinde bulunan **tr_TR.aff** ve 
**TS_Corpus_Turkish_Word_List.zip** dosyalarını indirip zip olanları 
çıkarmanız gerekmektedir. 