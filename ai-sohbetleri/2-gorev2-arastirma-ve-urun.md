# AI sohbeti 2 · Görev 2: araştırma ve ürün

Claude Code oturumundan çıkarıldı. Kullanıcı mesajları, Claude'un cevapları ve sorulan karar soruları kaldı. Araç çağrıları, dosya çıktıları ve sistem notları çıkarıldı.

---

### Kullanıcı · 13:05

freya_fde_case görev 2 için şu linki okumanı istiyorum, bazı terimler var tam anlayamadım https://www.backbase.com/blog/ai-banking-trends-2026. önerilerine açığınm

### Claude

Önce Freya notlarımı okuyup Backbase yazısını çekiyorum. Sonra terimleri görev 2 bağlamında açıklayacağım.

Makaleyi tam okudum: Backbase'in "10 AI banking trends reshaping the industry in 2026" yazısı, 5 Mayıs 2026. Case PDF'inde görev 2'nin metnine de baktım. Dikkatimi çeken bir şey var: PDF'in başlığı "AI-native bir banka" ve bu ifade makalenin 2. trendinin tam kendisi. Case aynı kelimelerle yazılmış, o yüzden bu terimleri bilmek anlatım videosunda da işine yarar.

## Makalenin ana fikri

**"Sorun model değil, altındaki mimari."** 10 trendin hepsi aynı yere bağlanıyor. AI'ı birbirinden kopuk eski sistemlerin üstüne eklersen denemede çalışır, gerçek kullanımda tıkanır. Çözüm olarak ortak veri ve ortak kurallar katmanı öneriyor. Bu da Backbase'in sattığı ürün.

## Terimler

**Mimari ve AI kavramları**
- **Agentic AI / AI agent:** Sadece cevap veren değil, işi adım adım planlayıp araç çağırarak yapan AI. Görev 1'deki asistanın bir agent: konuşuyor, servisi çağırıyor, randevu yazıyor.
- **AI-native ve AI-powered:** AI-powered, var olan sisteme sonradan eklenmiş AI demek, örneğin eski bir uygulamaya eklenmiş chatbot. AI-native ise süreci baştan AI yürütecek diye tasarlamak demek. İnsanlar yalnız istisnalarla uğraşır.
- **Orchestration / front-to-back orchestration:** Birden çok adımı ve sistemi tek akışta yönetmek. Front-to-back, başvurudan paranın hesaba geçmesine kadar her şeyin tek iş akışında olması. Makaledeki karşı örnek: "e-postayla birbirine bağlanmış beş sistem".
- **Systems of record / core systems:** Resmi kaydın tutulduğu çekirdek sistemler (core banking, hesap defteri).
- **Control plane:** Diğer sistemlerin üstünde durup kimin ne yapabileceğini yöneten katman. Kubernetes'teki control plane ile data plane ayrımıyla aynı fikir.
- **Single source of truth / unified customer view:** Müşteri hakkında tek ve tutarlı kayıt. Makaledeki örnek: "birbirini tutmayan yedi müşteri şeması".
- **Guardrails:** AI'ın yapabileceklerine konan sınırlar. Görev 1'deki iki kararın tam olarak bu: doğum tarihi LLM'e gitmiyor, kapasiteyi veritabanı kısıtları koruyor.
- **Governed autonomy levels:** AI'a yetkiyi kademe kademe vermek: önce yalnız "öner", sonra "insan onaylarsa yap", en son "kendin yap, sonra raporla".
- **Intent → policy-bound action:** Müşteri ne istediğini söyler (intent). LLM bunu anlar, bankanın kuralları da hangi işlemin yapılabileceğine karar verir.
- **Audit trail / evidence chain:** Her işlemin kim, ne, neden kaydı. Denetçi sonradan "bu karar neden verildi?" diye sorabilmeli.
- **Authorized, traceable, revocable:** Yetkili, izlenebilir, geri alınabilir.
- **Linear scaling ve elastic operations:** Linear'da müşteri iki katına çıkınca personel de iki katına çıkar. Elastic'te AI kapasitesi artar, personel aynı kalır.
- **10x bank / unconstrained banking:** Accenture'ın terimleri. Küçük bir ekibin çok sayıda AI agent'ı yönettiği banka.
- **Progressive modernization:** Her şeyi bir anda değiştirmek yerine alan alan dönüştürmek: önce müşteri edinimi, sonra kredi, sonra diğerleri.

**Bankacılık süreç terimleri**
- **KYC / KYB:** Müşterini Tanı. Türkiye'de MASAK mevzuatına giriyor. KYB şirketler için yapılır: vergi levhası, imza sirküleri, ticaret sicil gazetesi, ortaklık yapısı.
- **Onboarding:** Müşteri edinimi, hesap açılışı.
- **Origination:** Kredinin başvurudan kullandırıma kadar geçtiği süreç.
- **Underwriting:** Kredi değerlendirmesi. Riski ölçüp evet, hayır ya da limit kararı vermek.
- **Credit decisioning:** Kredi karar süreci.
- **Pre-approval:** Ön onaylı kredi.
- **Straight-through processing (STP):** İnsan dokunmadan baştan sona otomatik yürüyen işlem. Sorunsuz vakalar böyle biter.
- **Exception handling:** Kurala uymayan vakaları ayırıp ayrıca ele almak.
- **RM (relationship manager):** Kurumsal ve ticari müşteri temsilcisi.
- **Cross-sell:** Var olan müşteriye ek ürün satmak.
- **Account takeover:** Hesabın dolandırıcılar tarafından ele geçirilmesi.
- **Synthetic identity:** Gerçek ve uydurma bilgiler karıştırılarak üretilmiş sahte kimlik.
- **Behavioral biometrics:** Kişiyi yazma ritminden, ekranı kaydırma ya da telefonu tutma biçiminden tanımak.
- **Multimodal threat detection:** Davranış, belge ve ses/video deepfake kontrolünü birlikte yapmak.

**Metrikler**
- **Time-to-revenue:** Başvurudan, müşterinin bankaya gelir getirmeye başlamasına kadar geçen süre.
- **Time-to-yes:** Kredi başvurusundan olumlu karara kadar geçen süre.
- **Conversion:** Başvuranların ne kadarının müşteriye dönüştüğü.
- **Drop-off:** Süreci yarıda bırakanların oranı.
- **CLV:** Müşteri yaşam boyu değeri.
- **North star metric:** Ekibin her kararda baktığı ana metrik.

**Backbase'in ürün adları (genel terim değil, pazarlama)**
- Customer State Graph, Decision Token, Relationship Intelligence, Assist/Coach mode, Banking OS, Delivery Factory.
- Videoda bunları yerleşik kavram gibi kullanma, arkalarındaki fikri kendi kelimelerinle anlat. Örneğin Decision Token aslında şu: her işlem için hangi kuralın uygulandığı, işlemi kimin yaptığı (insan mı agent mı) ve hangi bağlamda yapıldığının kaydı.

## Eleştirel okuma

- **Bu bir satıcı blogu.** Her trend sonunda "ortak katman lazım" sonucuna, yani Backbase'in ürününe varıyor.
- **Rakamların çoğu kaynaksız:**
  - "150+ banka uygulaması"
  - "RM'lerin zamanının %30'undan azı müşteriyle geçiyor"
  - "%10-15 daha yüksek dönüşüm, %25-35 maliyet düşüşü"
  - "Şimdi başlayanlar 18-24 ay geride"
  - "AI projelerinin %85'i canlıya çıkmıyor" rakamı da Backbase'in kendi başka yazısına bağlanıyor.

  Videoda bu rakamları kullanacaksan kaynaksız olduklarını söyle ya da hiç kullanma.
- **Bence en önemli nokta:** makale eski bankalar için yazılmış. Saydığı sorunlar eski sistemler, kopuk yapılar, yedi ayrı şema. Case'teki banka ise **yeni açılmış**, eski sistemi yok. Yani makalenin dertlerinin yarısı senin bankanda yok. Senin bankanın darboğazları başka yerde:
  - AI'ın kararlarına güvenmek ve bu kararların hesabını verebilmek
  - İstisnalarda insanın rolü
  - Düzenlemeler: BDDK, KVKK, MASAK

  Bu ayrım kendi görüşünün başlangıç noktası olabilir.

## Önerilerim

**Görev 1 zaten makalenin ana fikrinin küçük bir örneği.** Kararlarına bak:
- Kapasiteyi LLM değil veritabanı koruyor.
- Tool'lar customer_id almıyor.
- Doğum tarihi LLM'e hiç gitmiyor.
- Sığmayan müşteri için zincir hazır: bu haftanın bekleme listesi → gelecek hafta önceliği → operasyona kapasite talebi.

Bunların hepsi "LLM niyeti anlar, kararı kurallar verir" fikri. Videoda görev 1'den görev 2'ye geçişi bunun üzerine kurabilirsin.

**Ürün önerim: operasyon / istisna masası.** AI-native bankada az sayıdaki çalışanın kullandığı ekran.
- **Kimin için:** Bankanın küçük operasyon ve uyum ekibi. 10x bank'teki "küçük ekip" bunlar.
- **Hangi işi görüyor:**
  - Agent'lar sorunsuz vakaları kendileri bitirir.
  - Yetkilerini aşan her şey bu masaya düşer: kapasite yetmedi, belge şüpheli, kurallar çelişiyor. Her vaka bağlamıyla ve önerilen aksiyonla birlikte gelir.
  - İnsan onaylar, reddeder ya da işlemi geri alır.
  - Her aksiyon için hangi kural, kim, hangi bağlam kaydı tutulur. Bu, Decision Token fikrinin senin versiyonu olur.
- **Demo verisi hazır:** Görev 1'deki Kadıköy taşması (3 müşteri, 2 yer) masaya ilk istisna olarak düşebilir. İki görev böylece tek hikâyeye dönüşür: "Müşterinin konuştuğu agent'ı kurdum, sonra o agent'ı denetleyen insanların ekranını tasarladım."
- **Bilerek dışarıda bırakılabilecekler:** Diğer agent'lar (mock olur), gerçek core banking entegrasyonu, rol ve yetki yönetimi, kredi kararı.
- **2 saate sığması için:** Tek sayfalık tıklanabilir bir HTML mock yeter. Görev 1'deki SQLite'tan gerçek bir istisna okuyabilirsen artı puan.

**Alternatifler:**
- **KOBİ onboarding agent'ı (trend 3):** Vergi levhası, imza sirküleri ve sicil gazetesini okuyup KYB dosyası hazırlar, tutarsızlıkları işaretler. Demosu görsel olarak güçlü ama görev 1'le bağı zayıf.
- **Sesli kanalda deepfake'e karşı kimlik doğrulama (trend 9):** Görev 1'de kimliği doğum tarihiyle doğruluyorsun, sesli bankacılıkta bu zayıf kalır. Videodaki "gerçek bankada açmadan önce ne eklerdin?" sorusuna doğrudan cevap olur. Ama mock ile göstermesi zor.

Benim tercihim istisna masası. Değerlendiricilerin baktığı muhakeme, iki görev birbirine bağlandığında en net görünür. Ama karar senin. İtiraz edersen tartışalım.

## Süreçle ilgili iki not

1. Case "AI sohbetlerini de gönder" diyor, bu sohbet de o kayda girecek. Bir fikre katılıyor ya da itiraz ediyorsan nedenini kısaca buraya yaz. "Fikre adım adım nasıl vardın?" sorusunun kanıtı bu satırlar olacak.
2. Tek bir satıcı blogu araştırma için zayıf kalır. İstersen makalenin dayandığı raporları (Accenture, Forrester, Deloitte, Gartner 2026) ya da karşıt görüşleri bulup özetleyebilirim.

result: Backbase'in "AI banking trends 2026" yazısındaki terimleri Türkçe açıkladım; yazının kaynaksız rakamlarla dolu bir satıcı blogu olduğunu ve yeni açılmış bir banka için değil eski bankalar için yazıldığını gösterdim; görev 2 için görev 1'le bağlantılı bir "operasyon / istisna masası" ürünü ve iki alternatif önerdim.

---

### Kullanıcı · 13:15

şuanda para transferi, hesap açımı, limit yükseltme talebi, kart talebi gibi işlemlerin hespi e-bankacılık uygulamalarından yapılıyor, bunu sadece telefon görüşmesiyle otomatize hale getirebilir miyiz?

### Claude

Bu soru makaledeki 7. trendle ("Conversational Banking uygulamanın yerini alıyor") örtüşüyor. Cevabı netleştiren asıl konu mevzuat, o yüzden önce BDDK'nın telefon bankacılığı ve uzaktan hesap açma kurallarını kontrol ediyorum.

Kısa cevap: **çoğunu evet, ama yalnızca telefon görüşmesiyle değil.** Ses, müşterinin ne istediğini anlamak için çok iyi bir arayüz. Ama işlemi yapma yetkisini ses vermemeli. Bunu iki BDDK yönetmeliği belirliyor, ikisini de kontrol ettim:

1. **Telefon bankacılığı da elektronik bankacılık sayılıyor.** Bilgi Sistemleri ve Elektronik Bankacılık Hizmetleri Yönetmeliği (2020) telefon bankacılığını internet ve mobil bankacılıkla aynı kapsama alıyor. Birbirinden bağımsız en az iki bileşenle kimlik doğrulama istiyor; bakiye görmek gibi finansal olmayan işlemlerde bile. Anne kızlık soyadı hiçbir aşamada doğrulama için kullanılamıyor.
2. **Hesap sesle açılamaz.** Uzaktan Kimlik Tespiti Yönetmeliği (Mayıs 2021) şunları istiyor: görüntülü görüşme, kimlik kartının çipinin NFC ile okunması, yüz eşleştirme ve canlılık kontrolü. Görüşmeyi de eğitimli bir müşteri temsilcisi yürütüyor.

Bulduğum kaynaklar 2020-2021 tarihli metinler ve haberler, sonraki değişiklikleri doğrulamadım. Videoda kullanmadan önce güncel metne bak.

## İşlem işlem

- **Bakiye ve işlem sorgulama:** Evet, iki bileşenli doğrulamadan sonra.
- **Kart talebi:** Evet. Asıl kontrol teslim anında: kart kayıtlı adrese gider ve kimlik görülerek verilir. Bu, görev 1'deki kuralın aynısı.
- **Limit artırımı:** Talep sesle alınabilir, kararı kredi kuralları verir. Ama hesabı ele geçiren dolandırıcının ilk yaptığı iş genelde limiti artırmak. O yüzden ek doğrulama ve müşteriye bildirim gerekir.
- **Kayıtlı alıcıya küçük tutarlı transfer:** Evet.
- **Yeni alıcıya ya da yüksek tutarlı transfer:** Ses işlemi başlatır, onay ikinci bir kanaldan gelir. Ses klonlamak artık ucuz, sesin kendisine güvenilemez.
- **Hesap açılışı:** Hayır. Asistan süreci anlatıp görüntülü görüşmeye yönlendirebilir.

## Asıl zor kısım: iki bileşen ne olacak?

- **Arayan numara tek başına bileşen sayılmaz.** Numara kolayca taklit edilebiliyor (spoofing).
- **Asistanın SMS kodunu sesli istemesi kötü bir yöntem.** Dolandırıcılar da tam olarak "gelen kodu söyleyin" diyor. Bankanın kendi asistanı bunu isterse "kodunuzu kimseye söylemeyin" uyarısı boşa çıkar.
- **Uygulama gerektirmeyen seçenek:**
  - Müşteri PIN'i telefonun tuşlarıyla girer. Bu "bildiği şey" ve hiç sesli söylenmiyor.
  - Banka kapatıp kayıtlı numarayı geri arar. Bu da "sahip olduğu SIM".
  - Böylece iki bağımsız bileşen olur. Yönetmeliğin SIM değişikliğinden sonra SIM'e dayalı bileşeni 90 gün kullanmamayı öngördüğüne dair bir haber var, ama tam şartını doğrulamadım. Bu yöntemin gerçek bir bankada kabul edilip edilmeyeceği de mevzuattan kontrol edilmeli.
- **Uygulaması olan müşteri için daha basit:** Kayıtlı cihaza push bildirimiyle onay.

## Bence ürün fikri burada

- **Doğal hedef kitle:** Uygulama kullanamayan ya da kullanmak istemeyenler: yaşlılar, görme engelliler.
- **Ama:** Kendini polis ya da savcı olarak tanıtıp "hesabınız tehlikede, parayı şu IBAN'a aktarın" diyen dolandırıcıların ana hedefi de tam bu grup. Yani sesli bankacılıktan en çok faydalanacak kişi, en çok risk altındaki kişi.

Sesli asistan burada uygulamanın yapamadığı bir şey yapabilir. Bu dolandırıcılıklarda parayı müşteri kendisi gönderiyor ve uygulama yalnızca tutarı ve IBAN'ı görüyor. Konuşma ise ipucu taşır: aciliyet, yeni bir IBAN, alışılmadık bir tutar, "polis söyledi" gibi sözler. Asistan durup "Bu parayı göndermenizi biri mi istedi?" diye sorabilir, işlemi bekletebilir ya da bir insana devredebilir. Böylece sesin zayıf yanı, yani dolandırıcılığa açık olması, ürünün güçlü yanına döner.

Ürünü böyle tanımlarsan:
- **Kimin için:** Uygulama kullanmayan, dolandırıcılık riski yüksek müşteriler.
- **Hangi işi görüyor:** Günlük işlemleri telefonla yaptırır, riskli olanları durdurur.
- **Çekirdeği:** Ses teknolojisi değil. Her işlem için risk seviyesine göre hangi doğrulamanın gerektiğini söyleyen bir yetki tablosu, bir de dolandırıcılık ipuçları.
- **Bilerek dışarıda bırakılanlar:** Hesap açılışı (mevzuat görüntülü görüşme istiyor), gerçek ses biyometrisi, gerçek EFT/FAST entegrasyonu.
- **Mock için:** Yetki tablosu ekranı ve üç senaryo:
  - Kayıtlı alıcıya transfer
  - Yeni alıcıya yüksek tutarlı transfer (ikinci onay istenir)
  - Dolandırıcılık şüphesi (işlem bekletilir, insana devredilir)

  Bekletilen işlem, daha önce önerdiğim istisna masasına düşebilir. Ama 2 saatte ikisini birden kurmaya çalışma.

**Dikkat edilmesi gereken bir risk:** Görev 2'yi de sesli asistan yaparsan değerlendirici bunu görev 1'in tekrarı gibi görebilir. Fark yaratan şey sesli arayüz değil, yetki tablosu ve dolandırıcılık tespiti olmalı. Videoda bunu açıkça söyle.

**Görev 1 için de bir sonucu var:** Orada kimliği doğum tarihiyle doğruluyorsun. Bu, yönetmeliğin iki bileşen şartını karşılamıyor. Videodaki "gerçek bankada açmadan önce ne eklerdin?" sorusuna hazır bir cevap.

Senin karar vermen gereken soru şu: **hedef kullanıcının elinde bankanın uygulaması var mı?** Varsa ikinci onay push bildirimiyle kolayca çözülür. Yoksa geri arama ve PIN gibi bir tasarım gerekir; ürün daha özgün olur ama yapması daha zor.

Kaynaklar:
- [Bankacılıkta ıslak imza zorunluluğu resmi olarak kalktı (Webrazzi)](https://webrazzi.com/2021/04/01/bankacilikta-islak-imza-zorunlulugu-resmi-olarak-kalkti/)
- [Bankalarca uzaktan kimlik tespiti nasıl olacak (Alomaliye)](https://www.alomaliye.com/2021/04/01/bankalarca-uzaktan-kimlik-tespiti-nasil-olacak/amp/)
- [BDDK'dan Bilgi Sistemleri ve Elektronik Bankacılık Hizmetleri Hakkında Yönetmelik (Bloomberg HT)](https://www.bloomberght.com/bddk-dan-bankalarin-bilgi-sistemleri-ve-elektronik-bankacilik-hizmetleri-hakkinda-yonetmelik-2249537)
- [Elektronik bankacılık: e-sözleşme, kimlik doğrulama ve işlem güvenliği (Alomaliye)](https://www.alomaliye.com/2023/03/27/elektronik-bankacilik-hizmetleri-e-sozlesme-kimlik-dogrulama-ve-islem-guvenligi/)
- [Kızlık soyadı sorma dönemi bitiyor (Hukuki Haber)](https://www.hukukihaber.net/kizlik-soyadi-sorma-donemi-bitiyor)

result: Hesap açılışı dışındaki işlemler (transfer, kart talebi, limit artırımı) telefonla otomatikleştirilebilir, ama BDDK telefon bankacılığında iki bağımsız bileşenli doğrulama istiyor, uzaktan hesap açılışı ise görüntülü görüşme ve NFC şartı yüzünden sesle yapılamıyor; görev 2 için yaşlı ve uygulama kullanmayan müşterilere yönelik, dolandırıcılığı konuşmadan yakalayan bir sesli bankacılık ürünü önerdim.

---

### Kullanıcı · 13:19

bu fikir aklımızda bulunsun şimdilik. blogdaki bütün maddeleeri tek tek yaz bana

### Claude

İki şeyi yapıyorum: sesli bankacılık fikrini Freya hafıza notuna görev 2 adayı olarak ekliyorum, sonra makalenin 10 maddesini tek tek yazıyorum.

Sesli bankacılık fikrini ve istisna masası fikrini Freya notlarına görev 2 adayı olarak kaydettim, BDDK bulgularıyla birlikte. Sonraki oturumlarda da hatırlanacak.

Makalenin bütün maddeleri:

## Giriş
- 2025'te AI denemeleri yapan bankaların çoğu 2026'da sorunun model değil, altındaki mimari olduğunu görüyor.
- Gartner'a göre AI agent'lar ve otomatik yürüyen operasyonlar bankacılıkta deneme aşamasından gerçek kullanıma geçiyor.
- Öne geçen bankalar en iyi algoritmaya sahip olanlar değil, birleşik bir altyapıya sahip olanlar.
- 10 trendin ortak noktası: bankalar AI'ı birbirinden kopuk sistemlerin üstüne ekledi.
- Makale trendlerin "150'den fazla banka uygulamasından" çıktığını söylüyor, kaynak vermiyor.

## 1. Agentic AI abartıdan gerçek kullanıma geçiyor
- AI agent'lar kontrollü ortamlardan gerçek banka operasyonlarına geçiyor. Accenture buna "unconstrained banking" diyor: küçük ekipler AI çalışanlarını yönetiyor.
- Zor olan tek bir agent kurmak değil. Zor olan, bilgiyi birbiriyle paylaşan, aynı kurallara uyan ve çekirdek sistemlere çelişkili veri yazmayan agent'lar kurmak.
- Kazanan bankalar agent'ları ortak bir operasyon katmanından yönetiyor. Her agent müşterinin aynı güncel bilgisini görüyor, aynı yetki kurallarına uyuyor, yaptığı her şey denetim kaydına yazılıyor.
- Bu katman yoksa agent sayısını artırmak hataları da çoğaltıyor.

## 2. AI-native mimari, sonradan eklenmiş AI'ın yerini alıyor
- Gartner: AI agent'lar müşteri deneyimini ancak altyapı destekliyorsa değiştirebiliyor.
- Eski sistemlerine AI ekleyen bankalar bir sınıra takılıyor: model demoda çalışıyor, gerçek kullanımda tıkanıyor. Üç nedeni var:
  - Veri dağınık.
  - Kararı kimin verdiği belirsiz.
  - Sistemleri birbirine bağlamanın maliyeti yüksek.
- Makalenin önerdiği çözüm "AI-native Banking OS": kayıt sistemlerinin üstünde durup işleri onlar arasında yürüten bir katman. Müşteri verisi ve karar yetkisi için tek bir doğru kaynak sağlıyor.
- 2026'da veri ve iş akışı altyapısını yeniden kuran bankalar, sonraki AI projelerini savunmakla daha az uğraşacak.

## 3. Agentic onboarding, müşterinin gelir getirmeye başlamasını hızlandırıyor
- Bireysel ve kurumsal müşteri edinimi pahalı ve zahmetli. Büyük bankalarda yalnızca KYB/KYC incelemeleri yılda "yüz milyonlarca" dolara mal oluyor. Maliyetin çoğu üç işten geliyor:
  - Verinin elle toplanması
  - Belgelerin sisteme yeniden girilmesi
  - İşin sistemler arasında taşınması
- Agentic onboarding, belgenin alınmasından hesabın açılmasına kadar bütün kanıt toplama sürecini otomatikleştiriyor.
- Makaleye göre bu, bankaların şu anda yapabileceği en yüksek getirili AI yatırımlarından biri. İddia edilen sonuçlar:
  - Gelir getirmeye başlama süresi haftalardan günlere iniyor.
  - Başvuruyu yarıda bırakanların oranı düşüyor.
  - Operasyon ekibi başvuruları baştan kurmak zorunda kalmıyor.
- Sorunsuz vakalar insan dokunmadan (STP) bitiyor, gerisi akıllı istisna yönetimine gidiyor.

## 4. GenAI müşteri temsilcilerini daha verimli yapıyor
- Kurumsal bankalarda müşteri temsilcileri (RM) zamanlarının %30'undan azını müşteriyle konuşarak geçiriyor. Gerisi sistemler arasında gidip gelmek, belge hazırlamak ve iç süreçlerle geçiyor. Bu rakamın kaynağı verilmemiş.
- GenAI hazırlık işini üstleniyor: görüşmeden önce müşterinin portföyündeki riskleri ve ek ürün satışı fırsatlarını çıkarıyor.
- Kazanç veri altyapısına bağlı. Müşteri, hesaplar, geçmiş ve risk için tek bir doğru kaynak gerekiyor. Backbase bunu "Relationship Intelligence" adıyla satıyor.

## 5. AI ile kredi kararı, kredi vermeyi büyük ölçekte hızlandırıyor
- Deloitte'un 2026 görünüm raporu operasyonlarda AI agent kullanımını belirleyici bir adım olarak görüyor. Makaleye göre ekonomik getirinin en yüksek olduğu alan kredi kararı.
- AI destekli kredi değerlendirmesi olumlu karar süresini kısaltıyor, ön onayları müşteri istemeden çıkarıyor ve istisnaları ele alıyor.
- Bunu iyi uygulayan bankalarda %10-15 daha yüksek dönüşüm ve kredi verme maliyetinde %25-35 düşüş iddia ediliyor. Kaynak belirtilmemiş.
- Tasarım ilkesi "front-to-back orchestration": başvuru, belge toplama, kredi değerlendirmesi ve paranın hesaba geçmesi tek bir koordineli akışta yürüyor. Karşı örnek: "e-postayla birbirine bağlanmış beş ayrı sistem".
- Sonuç: karar süresi günlerden saatlere iniyor ve her karar sonradan denetlenebiliyor.

## 6. Mevzuata uyum kontrolü olaydan sonra değil, anında yapılıyor
- Forrester'ın 2026 tahminleri, uyum işi için özel görevli AI agent'ları belirleyici bir kullanım alanı olarak görüyor.
- AI işlemleri anında izliyor, olağan dışı durumları kural ihlaline dönüşmeden yakalıyor ve her işlem için tam bir kanıt zinciri tutuyor. Makaleye göre bu artık sadece risk yönetimini iyileştirmek değil, rekabette kalmanın şartı.
- Bunu güvenli kılan şey bir denetim katmanı. Bir insanın, bir iş akışının ya da bir AI agent'ın yaptığı her işlem bir "Decision Token" taşımalı. Bu kayıtta üç şey var:
  - Uygulanan kural
  - İşlemi yapanın kim olduğu
  - Kararın bağlamı
- Denetlenebilirlik baştan sisteme konmazsa banka otomasyon yaparken yeni mevzuat riskleri yaratıyor.
- **Bizim için:** İstisna masası fikrindeki "kural, aktör, bağlam kaydı" bu maddenin karşılığı.

## 7. Konuşarak bankacılık, işlem uygulamasının yerini alıyor
- Forrester: AI agent'lar müşteriyle etkileşimi üstlendikçe insanların banka web sitelerini ziyaretinde %20 düşüş bekleniyor.
- Bakiye sorma, ödeme başlatma, itiraz açma ve ürünlere göz atma gibi rutin işler menülü uygulamalar yerine doğal dille yapılıyor. Müşteri ne istediğini yazıyor ya da söylüyor, banka sistemi bunu kuralların izin verdiği bir işleme çeviriyor.
- İki mod var:
  - **Assist:** İşi menülerde gezinmeden hızlıca yapar.
  - **Coach:** Müşterinin finansal durumunu, seçeneklerini ve kararlarını anlamasına yardım eder.

  İki mod da müşterinin aynı güncel bilgisi üzerinde çalışıyor.
- Konuşarak bankacılığı diğer kanallardan kopuk ayrı bir kanal olarak kuran bankalar, kanalların birlikte çalışmasından gelen değeri kaçırıyor.
- **Bizim için:** Sesli bankacılık fikrimiz tam bu madde. Makale güvenlikten ve kimlik doğrulamadan hiç bahsetmiyor; bizim fikri farklı kılan da orası.

## 8. Birleşik veri, dağınık AI sistemlerinden daha iyi sonuç veriyor
- Deloitte: Kırılgan veri altyapısı, AI'ı büyük ölçekte kullanmanın önündeki ana engel.
- Makaleye göre asıl darboğaz model kalitesi değil, "birbirini tutmayan yedi müşteri şeması". AI ya eksik bilgiyle çalışıyor ya da işlem gücünün çoğunu tutarsız kayıtları eşleştirmeye harcıyor.
- Çözüm ortak bir müşteri veri modeli. Backbase'in "Customer State Graph"ı şunları tek modelde birleştiriyor:
  - Müşteriyle ilişki verisi
  - İşlem geçmişi
  - Açık talepler
  - Davranış sinyalleri

  Böylece AI tespit etmekle kalmayıp koordineli bir şekilde harekete geçebiliyor.

## 9. Dolandırıcılık tespiti kimlik doğrulama ve uyumla birleşiyor
- Deepfake ile yapılan kimlik dolandırıcılığı, AI ile üretilmiş sahte kimlikler ve organize hesap ele geçirme saldırıları artık tek bir tehdit alanı oluşturuyor.
- Finastra'nın 2026 AI görünüm raporu: Davranışsal biyometri, belge doğrulama ve deepfake tespitini birlikte kullanan tehdit tespiti standart hale geliyor.
- Bankaların çoğu dolandırıcılık, kimlik ve uyum için hâlâ ayrı sistemler kullanıyor.
- Bu açığı kapatan bankalar dolandırıcılık tespitini müşteri edinimi ve müşteri hizmetleriyle aynı katmana koyuyor. Tespit tek seferlik bir kontrol değil, her etkileşimde sürekli çalışan bir sinyal. Böylece olağan dışı durumlar müşteriyle ilişkinin her aşamasında yakalanıyor.
- **Bizim için:** Sesli bankacılıktaki ses klonlama riski ve konuşmadan dolandırıcılık sinyali yakalama fikri bu maddeye dayanıyor.

## 10. "10x banka" çalışma modeli şekilleniyor
- Accenture'ın "10x bank" kavramı öncü bankalarda görülmeye başladı: küçük ekipler AI agent'ları yöneterek kapasitelerini katlıyor.
- Değişim şu: eskiden daha çok müşteri daha çok personel demekti. Şimdi daha çok müşteri, aynı kurallar altında daha çok AI kapasitesi demek. Böylece maliyetler aynı oranda artmadan işlem hacmi büyüyor. Makaleye göre AI dönüşümünün asıl ekonomik kazancı bu.
- Agent'lar arasında ortak bilgi ve koordinasyon yoksa birbirleriyle çelişiyorlar ve işlemlerin izi sürülemiyor.
- Bu altyapıyı kuran bankalar müşteri hizmetlerinde, kredi vermede ve konuşarak bankacılıkta agent'ları koordineli şekilde çalıştırıyor.
- 2024'te başlayanlar önde. Makaleye göre "şimdi başlayanlar 18-24 ay geride", kaynak yok.
- **Bizim için:** İstisna masası, bu "küçük ekibin" çalıştığı ekran.

## Sonuç: banka yöneticileri için anlamı
- Bankaların güçlü modellere erişimi var, ama çok azında bu modelleri müşteriyle doğrudan temas eden işlerde çalıştıracak mimari var.
- Çoğu banka iki uç arasında: bir bölümde çalışan agent'lar, başka bir bölümde dağınıklık.
- Makaleye göre "bankacılık AI projelerinin %85'i hiç canlıya çıkmıyor" ve neden neredeyse her zaman teknik değil, yapısal. Bu rakam Backbase'in kendi başka bir yazısına dayanıyor.

## Sık sorulan sorular bölümündeki ekler
- Agentic AI çok adımlı süreçler boyunca akıl yürütüyor. Belirlenmiş sınırlar (guardrails) ve kontrollü yetki seviyeleri içinde, her adımda insan onayı beklemeden çalışıyor.
- Denetim ilkesi: her işlem yetkili, izlenebilir ve geri alınabilir olmalı.
- Önerilen yol aşamalı dönüşüm, her seferinde bir alan. AI-native Banking OS, mevcut kayıt sistemlerinin üstünde onları yöneten katman ("control plane") olarak konumlanıyor.

Sayfanın kenarındaki "Augmented, not automated: keeping humans in the loop" gibi başlıklar makalenin metninde yok; sitedeki başka yazılara bağlantılar.

result: Backbase makalesindeki 10 trendin hepsi giriş, sonuç ve SSS bölümleriyle birlikte Türkçe olarak tek tek yazıldı; sesli bankacılık ve istisna masası fikirleri, BDDK bulgularıyla birlikte Freya hafıza notuna görev 2 adayı olarak kaydedildi.

---

### Kullanıcı · 13:28

10x banka modelinde, bankada çalışan birçok agent olucak, bu agentların hepsinin knowledge'ı nasıl sınırlandırılacak? yetkileri nasıl sınırlandırılacak? ya da birbirleri ile knowledge paylaşımı nasıl? sessionlar overload olursa çözüm ne? bilgi kaybı vs? ya da bu kadar knowledge'ı nasıl ve nerede tutacaklar.

### Claude

Kısa cevap: **Bilgi de yetki de agent'ın içinde değil, bankanın zaten denetlediği sistemlerde durmalı.** Model hiçbir şeyi kalıcı olarak "bilmez" ve hiçbir şeye "yetkili" olmaz. Her görev için gereken bağlamı alır, düşünür, izin verilen araçları çağırır, sonra unutur. Böyle kurulunca sorduğun soruların çoğu bildiğimiz yazılım sorularına dönüşüyor: yetkilendirme, veri erişimi, olay kaydı, ölçekleme.

```
 Müşteri / çalışan
        │
 Orkestratör ── görev başına bağlamı hazırlar, oturumu yönetir
        │
 Agent (LLM) ── yalnızca düşünür, kalıcı hafızası yok
        │  tool çağrısı
 Tool katmanı ── kimlik, yetki kontrolü (kural motoru), maskeleme, kayıt
        │
 Kayıt sistemleri · olay günlüğü · bilgi bankası · kurallar
```

## 1. Bilgi nasıl sınırlanır?

Üç tür bilgi var, her biri farklı korunur:

- **Kurumsal bilgi** (ürünler, prosedürler, mevzuat): Herkes okuyabilir. Versiyonlu bir doküman deposunda durur, agent arama ile çeker (RAG).
- **Müşteri verisi:** En hassas olanı, yalnızca ihtiyaç kadar verilir.
- **Görev bağlamı:** Sadece o işe ait bilgi.

Asıl kural şu: **agent veriyi kendisi çekmez, orkestratör ona verir.** Orkestratör göreve gereken en az bağlamı hazırlar. Bazı alanlar ise modele hiç gitmez (doğum tarihi, TCKN, tam kart numarası). Bunlarla ilgili kontrol tool katmanında yapılır, model sadece "doğrulandı: evet/hayır" sonucunu görür.

Görev 1'de bunu zaten yaptın: agent müşteri tablosunun tamamını görmüyor, müşteri sunucuda oturuma bağlı ve doğum tarihi LLM'e hiç gitmiyor. Bu, KVKK'daki "amaçla sınırlılık" ilkesinin teknik karşılığı.

Türkiye'ye özgü bir sınır daha var. Bildiğim kadarıyla Bankacılık Kanunu ve BDDK yönetmeliği, bankanın birincil ve ikincil sistemlerinin yurt içinde olmasını istiyor. Yani müşteri verisini yurt dışındaki bir LLM API'sine göndermek ciddi bir mevzuat sorusu. AI-native bir Türk bankası için "model nerede çalışıyor?" sorusu ilk sorulardan biri olur. Videoda kullanacaksan bunu metinden doğrula.

## 2. Yetki nasıl sınırlanır?

- **Agent'ın yetkisi, elindeki tool listesidir.** Tool'u olmayan işi yapamaz. Prompt'a "transfer yapma" yazmak yetki değildir: model bunu unutabilir, prompt injection ile atlatılabilir. Gerçek sınır sunucu tarafında, tool'un içinde olmalı.
- **Her agent'ın kendi kimliği olur,** bir servis hesabı gibi: rolü, limitleri, sürüm numarası. Örneğin kart teslim agent'ı randevu yazabilir ama para transferi yapamaz.
- **Agent müşteri adına, müşterinin yetkisiyle çalışır.** Müşteri kimliği LLM'in verdiği bir parametreden değil, oturumdan gelir. Model ne derse desin başka bir müşterinin verisine dokunamaz. Görev 1'de customer_id'nin tool'lara verilmemesi tam olarak bu.
- **Eşikler ve kademeli yetki kural motorunda durur,** prompt'ta değil. Örnek: 5.000 TL altı ve kayıtlı alıcıysa "yap", üstündeyse "öner, insan onaylasın". Bu kurallar versiyonlu olur, test edilebilir ve denetçi tarafından okunabilir. **Senin BRMS işin tam buraya oturuyor:** 10x bankada agent'ların yetki katmanı aslında bir kural motoru.
- **Dört göz ilkesi (maker-checker):** Yüksek riskli bir işlemi bir agent hazırlar, başka bir aktör onaylar. Bu, bankacılıkta zaten var olan bir kontrolün agent'lara uygulanması.
- **Her tool çağrısı kayda geçer:** hangi agent (sürümü ve model sürümüyle), kimin adına, hangi kural uygulandı, girdi neydi. Makaledeki "Decision Token" bu kayıt.

## 3. Agent'lar bilgiyi birbiriyle nasıl paylaşır?

- **Birbirleriyle doğrudan konuşarak paylaşmazlar.** Doğrudan sohbette bilgi kulaktan kulağa oyunundaki gibi bozulur ve denetlenemez. Paylaşım ortak kayıtlar üzerinden olur:
  - **Müşterinin güncel durumu:** kayıt sistemlerinde.
  - **Olay günlüğü:** Bir agent iş yaptığında olay yazar ("teslim Perşembe 09-13'e alındı"), diğer agent'lar gerektiğinde okur.
- **İş devri serbest metinle değil, yapılandırılmış bir vaka kaydıyla yapılır:** ne istendi, ne yapıldı, ne kaldı, kanıtlar neler. İstisna masasına düşen vaka da bu formatta olur.
- **Aynı kaydı iki agent değiştirmek isterse koordinasyonu LLM'ler değil veritabanı yapar:** transaction, koşullu UPDATE, kilit. Görev 1'deki kapasite koruması bunun örneği.
- **Paylaşılan bilgi de yetkiye tabidir.** Bankacılıktan iyi bir örnek: dolandırıcılık agent'ının "şüpheli işlem bildirildi" notu, müşteriyle konuşan agent'a gösterilmemeli. MASAK mevzuatında, şüpheli işlem bildirimi yapıldığının müşteriye açıklanması yasak. Konuşan agent bu notu görürse ağzından kaçırabilir.

## 4. Oturum dolarsa ya da sistem aşırı yüklenirse?

İki farklı sorun var.

**Bağlam penceresinin dolması:**
- **Bağlam bir çalışma masası, arşiv değil.** Kalıcı olması gereken her şey zaten başka bir yere yazılmış olmalı. Bağlam kaybolsa bile bilgi kaybolmamalı.
- **Uzun yaşayan, her şeyi bilen bir agent olmaz.** Her vaka için yeni, kısa bir oturum açılır ve bağlam kayıtlardan yeniden kurulur.
- **Uzun konuşmalarda eski turlar özetlenir, ama özet kayıplıdır.** O yüzden kritik bilgiler hiçbir zaman sadece konuşma geçmişinde durmaz: tutar, IBAN, müşterinin neyi kabul ettiği, doğrulamanın yapılıp yapılmadığı. Bunlar yapılandırılmış alanlarda tutulur. Özetleme sırasında bir tutarın değişmesi felaket olur.
- **Konuşma yarıda koparsa işlemler iki kez yapılmamalı.** Her işleme bir idempotency anahtarı verilir. Örneğin transfer onaylandı ama bağlantı koptu: yeniden bağlanınca durum kayıttan okunur, transfer tekrar gönderilmez.

**Çok sayıda eşzamanlı oturum:**
- Klasik ölçekleme yöntemleri: durumsuz (stateless) çalışanlar, kuyruk, hız sınırı (rate limit), model sağlayıcı kotası.
- Aşırı yükte öncelik sırası olur: kart kapatma ve dolandırıcılık bildirimi önce işlenir, bilgi sorguları kuyrukta bekleyebilir.
- Model sağlayıcısı çökerse sistem çökmez, kontrollü şekilde geri çekilir: yedek modele geçer ya da "sizi geri arayalım" moduna düşer.

## 5. Bu kadar bilgi nerede tutulur?

| Ne | Nerede | Not |
|---|---|---|
| Resmi müşteri ve hesap verisi | Kayıt sistemleri (core banking) | Agent'lar okur, yalnızca tool üzerinden yazar |
| Kim ne yaptı | Değiştirilemez olay günlüğü | Hem denetim kaydı hem agent'lar arası paylaşım |
| Prosedür, ürün, mevzuat | Versiyonlu doküman deposu + arama | Her cevabın hangi sürümden geldiği kaydedilir |
| Yetki, limit, eşikler | Kural motoru (BRMS) | Prompt'ta durmaz |
| Agent tanımı (prompt, tool listesi, model) | Kod gibi git'te, onaylı değişiklikle | Görev 1'deki PROMPTS.md bunun küçük hali |
| Ses kayıtları ve konuşma dökümleri | Saklama süresi mevzuata göre olan arşiv | KVKK kapsamında |

**Bilginin tutulmaması gereken yer: modelin kendisi.** Müşteri verisiyle modeli eğitirsen (fine-tuning), o bilgi modelden geri silinemez. Bu da KVKK'daki silme hakkıyla çelişir. Müşteri bilgisi veritabanında durmalı, modelde değil.

## Görev 2'ye etkisi

Makale "ortak bir katman lazım" diyor ama bu katmanın içinde ne olduğunu söylemiyor. Bu cevap o boşluğu dolduruyor. Videodaki "gerçek bankada açmadan önce ne eklerdin?" sorusunun iskeleti de olabilir.

İki aday fikrini de güçlendiriyor:
- **İstisna masası:** Bu mimaride insanın devreye girdiği nokta.
- **Sesli bankacılık:** Yetki matrisi buradaki kural motoru katmanı.

Mevzuatla ilgili iki noktayı (verinin yurt içinde tutulması şartı ve MASAK'ın açıklama yasağı) bildiklerime dayanarak yazdım, bu turda doğrulamadım. Diğer her şey tasarım önerisi.

result: 10x bankada çok sayıda agent için bilgiyi, yetkiyi, agent'lar arası paylaşımı, oturum dolmasını ve bilginin nerede saklanacağını açıkladım: model durumsuz bir akıl yürütücü olarak kalıyor; bilgi kayıt sistemlerinde ve olay günlüğünde, yetki tool katmanında ve kural motorunda (BRMS) duruyor; iki mevzuat noktası henüz doğrulanmadı.

---

### Kullanıcı · 13:55

bankalarda kullanılan workflow/decision engine sistemlerinin/ürünlerinin çoğunda "ai node"'u yok, periyodik gerçekleştirilen bazı checklerde ya da iletişimlerde ai node'u otomatik görüşmeyi vs gerçkleştirip bilgileri flowa aktarabilir.

### Claude

Kendi alanından çıkan güçlü bir gözlem bu. Önce öncülünü kontrol ediyorum: büyük workflow ve karar motoru satıcıları 2025-2026'da "AI node" eklemiş mi? Fikrin özgün olup olmadığını bu belirleyecek.

Fikri Freya notuna "C" adayı olarak ekledim. Bence şu ana kadarki en güçlü aday bu.

## Öncül: kısmen doğru

Büyük global platformlar bu düğümü 2025'te eklemiş:
- **Camunda 8.8 "AI Agent connector":** LLM bir BPMN alt sürecinin içinde hangi adımı çağıracağını seçiyor. Camunda adımı yürütüyor, değişkenleri saklıyor, hata olursa yeniden deniyor, insan görevlerini yönlendiriyor.
- **Pega:** Infinity '26 sürümünde agent'ları ekledi; Aralık 2025'te müşteri yaşam döngüsü (onboarding, tarama, risk değerlendirmesi) ürününün agentic sürümünü çıkardı.
- **Pega'nın tezi seninkine çok yakın:** Akış tasarım aşamasında çiziliyor, agent'lar akışın içinde görev yapıyor ama yolu kendileri uydurmuyor.

Yani "akışa AI adımı koymak" artık yeni bir kategori değil. Ama büyük satıcıların aynı yöne gitmesi, fikrin doğru yönde olduğunu gösteriyor.

Senin fikrini farklı kılan şey ayrıntıda:
- Hazır gelen düğümler genel amaçlı: "LLM'i çağır, tool seçsin."
- Senin tarif ettiğin düğüm, **müşteriyle günlerce sürebilen bir konuşma yürütüp sonucu yapılandırılmış veri olarak akışa geri getiriyor.**

Bulduğum kaynaklarda bunu hazır sunan görmedim, ama aramam sınırlıydı. Türkiye'de bankaların kullandığı yerli ve eski karar motorlarında bu düğümün olmaması ise senin sahadan bildiğin bir şey; bunu ben doğrulayamam, sen videoda kendi gözlemin olarak anlatabilirsin.

## Neden doğru mimari

Önceki soruda sorduğun problemlerin çoğunu workflow motoru zaten çözüyor:

- **Bilgi kaybı ve dolan oturum:** Durum akışın değişkenlerinde saklanıyor. AI düğümü her denemede kısa ömürlü; bağlam kaybolsa da bir şey kaybolmuyor.
- **Uzun süren iletişim:** Müşteri telefonu açmazsa zamanlayıcı iki gün sonra yeniden dener. Müşteri geri ararsa mesaj bekleyen akış örneğine bağlanır (message correlation).
- **Yetki:** Düğüm yalnızca kendisine tanımlanan tool'ları çağırabilir. Kararı karar tablosu (BRMS) verir.
- **İnsan:** Human task kuyruğu, istisna masası fikrinin ta kendisi.
- **Denetim:** Her akış örneğinin geçmişi zaten tutuluyor.

İlke tek cümle: **AI kenarda algılar, kararı merkezdeki kural verir.** AI düğümü konuşmayı ya da belgeyi anlar, karar tablosu ne olacağına karar verir.

## Düğümün sözleşmesi (ürünün çekirdeği burası)

Örnek, periyodik KYC güncellemesi:

```yaml
dugum: periyodik_kyc_guncelleme
kanal: sesli_arama            # yedek kanal: sms
amac: "Adres, meslek ve gelir aralığı hâlâ geçerli mi, teyit et"
baglam: [ad, kayitli_ilce, meslek]   # TCKN ve doğum tarihi modele gitmez
araclar: [kimlik_dogrula]
deneme: {en_fazla: 3, aralik: 2g}
cikti:
  sonuc: TEYIT | DEGISTI | ULASILAMADI | REDDETTI | BELIRSIZ
  degisen_alanlar: [{alan, yeni_deger, musteri_acikca_onayladi: bool}]
  kayit: transcript_id, model_surumu, prompt_surumu
```

Karar tablosu da bu çıktıya göre ne olacağını belirler:
- `DEGISTI` ve meslek değişmişse → risk puanı yeniden hesaplanır
- Üç kez `ULASILAMADI` → human task açılır
- `BELIRSIZ` → human task açılır

Sözleşmenin üç katı kuralı:
1. **Şemaya uymayan çıktı akışa girmez.** Düğüm yeniden denenir ya da iş insana gider.
2. **`BELIRSIZ` geçerli bir sonuçtur.** Müşteri "belki Perşembe" dediyse düğüm bunu "Perşembe, onaylandı" diye kaydetmez.
3. **Düğüm karar vermez,** sadece bilgi toplar.

## Kullanım alanları

- **Periyodik KYC güncellemesi:** Müşterinin risk seviyesine göre belirli aralıklarla.
- **Erken tahsilat:** Ödeme 1-5 gün geciktiğinde arama yapılır ve ödeme sözü tarihi alınır. Akış o tarihte ödemenin gelip gelmediğini kontrol eder.
- **Şüpheli işlem teyidi:** "Bu işlemi siz mi yaptınız?" Cevap evet ya da hayır olur, kartın bloke edilip edilmeyeceğine kural karar verir.
- **Teslim edilemeyen kart:** Görev 1'in kendisi bu akışın ilk düğümü olur.
- **Kurumsal kredi takibi:** Periyodik mali tablo ve teminat belgesi istemek, gelen belgeyi okumak.

## Dikkat edilmesi gerekenler

- **Bankanın araması dolandırıcılık aramasına benziyor.** Müşterilere yıllardır "banka sizi arayıp bilgi istemez" deniyor. Bankanın AI'ı arayıp doğrulama sorusu sorarsa bu tam olarak dolandırıcıların yaptığı şeye benzer. Olası çözümler:
  - Giden aramada gizli bilgi istememek.
  - Aramadan önce uygulamaya "Bankanız sizi şu numaradan arayacak" bildirimi göndermek.
  - Ya da müşteriden bankanın resmi numarasını geri aramasını istemek.
- **Kimlik doğrulama:** Önceki cevaptaki iki bileşen şartı, bankanın aradığı müşteri için de geçerli.
- **İzin:** Pazarlama amaçlı aramalar İYS onayı gerektirir. Mevcut sözleşmeyle ilgili bilgilendirme aramalarının durumu genelde ayrı, ama bunu doğrulamadım.
- **Test:** Sonucu her seferinde aynı olmayan bir düğüm, her değişiklikten sonra bir senaryo setiyle test edilmeli. Görev 1'deki `simulate.py` tam olarak bu işi görüyor.

## Görev 2 açısından neden en güçlüsü

- **Görüşün sahadan geliyor.** Case'in "kendi görüşünü oluştur" isteğine en sahici cevap bu.
- **Backbase'e net bir karşı tezin var:** "Yeni bir Banking OS'a gerek yok. AI'ı bankanın zaten güvendiği workflow ve karar motoruna sınırlı bir düğüm olarak ekle." Pega'nın yaklaşımını da bu tezi destekleyen kanıt olarak gösterebilirsin.
- **Üç fikir tek üründe birleşiyor:**
  - Görev 1 → ürünün ilk düğümü
  - İstisna masası → human task kuyruğu
  - Sesli bankacılıktaki yetki matrisi → karar tablosu
- **2 saate sığacak mock:** Statik bir akış tuvali, AI düğümünün ayar paneli ve bir çalıştırma izi (konuşma dökümü → yapılandırılmış çıktı → tetiklenen kural → seçilen dal).

**Bir uyarı:** Bu fikri Cybersoft'taki işinden aldığın için, Freya'ya göndereceğin mock'ta şirketin ürününü, ekranlarını, kodunu ya da müşteri bilgilerini kullanma. Genel bir akış motoru üzerinden anlat.

Sana bir soru: demoda hangi periyodik süreci göstermek istersin? Ben teslim edilemeyen kartı öneririm. Görev 1'deki çalışan agent'ı gerçek bir düğüm olarak takabilirsin ve iki görev doğal olarak birbirine bağlanır.

Kaynaklar:
- [Camunda 8.8 docs: AI agents](https://docs.camunda.io/docs/8.8/components/agentic-orchestration/ai-agents)
- [Camunda 8.8 docs: AI Agent connector](https://docs.camunda.io/docs/8.8/components/connectors/out-of-the-box-connectors/agentic-ai-aiagent/)
- [Pega: Future of banking in an agentic world (PDF)](https://www.pega.com/system/files/resources/pdf/pega-pw25-future-banking-agentic-world.pdf)
- [Pega Smart Investigate agentic AI (Techzine)](https://www.techzine.eu/news/applications/134640/pega-smart-investigate-gets-agentic-ai-boost-for-faster-detection-of-payment-exceptions)
- [Pega agentic CLM launch, Aralık 2025 (BusinessWire)](https://www.businesswire.com/news/home/20251216099877/en/)

result: Workflow ve karar motoruna "AI düğümü" eklemek doğru yönde (Camunda 8.8 ve Pega genel agent düğümünü 2025'te ekledi), ama müşteriyle konuşup sonucu yapılandırılmış veri olarak akışa getiren düğüm daha dar ve hazır sunanını bulamadım; bunu görev 2'nin en güçlü adayı olarak önerdim, düğüm sözleşmesini ve kullanım alanlarını çıkardım ve Freya notuna "C" olarak kaydettim.

---

### Kullanıcı · 14:03

bankalar beni bazen arıyor, şöyle şöyle bi teklifimiz var size falan filan laga luga yapıyolar. kredi karıt teklifi vs vs. bu teklifler internal bi flowdan geçtikten sonra yapılıyor yüksek ihtimalle, biz target olarak zaten belliyiz, ama iletişimi call center yapıyor.

### Claude

Gözlemin doğru, ve bu C fikrinin tam oturduğu yer: hedefleme zaten otomatik, insan sadece son halkada. Bunu Freya notuna da ekliyorum.

Notu güncelledim. Tahminin büyük ihtimalle doğru; arkadaki yapı genelde şöyle işler (belirli bir bankanın içini bilmiyorum, bu tipik yapı):

```
Eğilim modeli ── bu müşteri kredi kartı alır mı? (skor)
      │
Karar motoru ── ön onaylı limit: KKB skoru, gelir tahmini, risk kuralları
      │
Kampanya yönetimi ── kime, hangi kanaldan, ne zaman? İYS izni var mı?
      │
Arama listesi ──► ÇAĞRI MERKEZİ (insan)  ◄── otomatik olmayan tek halka
      │
Sonuç kodu ── ulaşılamadı / ilgilenmedi / kabul etti / tekrar ara
      │
CRM ve akış devam eder
```

## Kritik nokta: çağrı merkezi zaten yapılandırılmış veri döndürüyor

Temsilci görüşmeyi bitirince bir **sonuç kodu** seçiyor. Bu, önceki mesajda tarif ettiğim düğüm sözleşmesinin ilkel hali. Yani AI düğümünün bağlanacağı yer hazır: insanın oturduğu koltuğa oturur, aynı sonuç kodlarını doldurur, akışın geri kalanı hiç değişmez. C fikri için başlamanın en kolay yeri bu, çünkü entegrasyon maliyeti neredeyse sıfır.

## Ama kendi kelimene bak: "laga luga"

Teklif aramalarının asıl sorunu maliyet değil, müşterilerin bu aramalardan hoşlanmaması. AI aramayı neredeyse bedava yaparsa bankalar daha çok arar ve spam artar. Yani **"çağrı merkezini AI ile değiştir" tek başına kötü bir ürün.** İyi ürün, AI ile aramanın kendisini düzeltmek:

- **Daha az ama doğru zamanda arama.** Listeyi baştan sona aramak yerine bir olaya bağlı arama yapılır. Örneğin müşteri yurt dışında harcama yaptıysa, yurt dışı komisyonu olmayan kart teklif edilir.
- **Sorulara gerçek cevap.** Aidat, faiz, yıllık maliyet: bu rakamlar akıştan okunur, model kendisi üretmez. Çağrı merkezinde "laga luga"nın kaynağı genelde temsilcinin sorulara net cevap verememesi.
- **"Hayır" geçerli bir sonuç.** Karar tablosu reddeden müşteriye bu ürünü örneğin 6 ay teklif etmez. Müşteri "beni bir daha aramayın" derse bu, tercih kaydına doğrudan yazılır.
- **Arayan kendini AI olarak tanıtır.** AB'nin AI Act'i de bunu istiyor.
- **Gizli bilgi istenmez.** Bankanın araması dolandırıcılık aramasına benzediği için başvuru telefonda tamamlanmaz. Müşterinin uygulamasına onay bildirimi gider, onay orada iki bileşenli doğrulamayla verilir.

## Satışa özel güvenlik önlemleri

- **Model pazarlık yapamaz.** Limit, aidat ve faiz karar motorundan gelir; model sadece onaylanmış teklifi anlatır.
- **Her arama otomatik denetlenir.** Arama bittikten sonra, müşteriye söylenen rakamlar teklifin gerçek parametreleriyle karşılaştırılır. Çağrı merkezleri genelde aramaların küçük bir kısmını dinleyebiliyor; AI ise her aramayı kontrol edebilir. Bu, insan temsilcilerin aramaları için de kullanılabilecek ayrı bir değer.
- **Kırılgan müşteriye satış yapılmaz.** Konuşmadan yaşlı olduğu ya da teklifi anlamadığı belli olan müşteri insana devredilir. B fikrindeki hedef kitleyle aynı hassasiyet.

Teklif düğümünün sözleşmesi şöyle olabilir:

```yaml
dugum: kredi_karti_teklif_aramasi
baglam: [ad, teklif_id]          # limit, aidat ve faiz tool'dan okunur, prompt'a yazılmaz
araclar: [teklif_detayi_getir, uygulamaya_onay_gonder, iletisim_tercihi_guncelle]
cikti:
  sonuc: KABUL | DUSUNECEK | RED | TEKRAR_ARA | ULASILAMADI | BIR_DAHA_ARAMA | INSANA_DEVRET
  tekrar_ara_zamani: tarih?           # yalnızca TEKRAR_ARA ise
  musteriye_soylenen_rakamlar: [...]  # aramadan sonra teklifle otomatik karşılaştırılır
```

## Demo için güçlü bir hikâye

Bu gözlem C'yi tek bir uçtan uca akışa dönüştürüyor: **aynı akışta iki AI düğümü, kartın bütün yaşam döngüsü.**

```
Hedefleme (karar tablosu) → AI teklif araması → KABUL → uygulamada onay
→ kart basımı → kurye → teslim edilemedi → AI teslim araması (Görev 1)
→ çözülemezse insan görevi (istisna masası)
```

Değerlendirici bunu bir chatbot olarak değil, bir platform olarak görür. Görev 1 de bu platformun gerçekten çalışan bir düğümü olur. Mock'ta teklif düğümünün çalışması gerekmez; konuşma dökümü ve sonuç kodu yeter.

Bir şeyi kontrol etmek istersen: teklif aramalarının İYS'deki "arama" iznine bağlı olduğunu biliyorum. Ama mevcut sözleşmeyle ilgili bilgilendirme aramalarıyla sınırın tam nerede olduğunu doğrulamadım.

result: Banka teklif aramalarında hedefleme ve ön onaylı limit zaten otomatik, yalnızca arama insanla yapılıyor ve çağrı merkezi sonucu zaten sonuç kodu olarak dönüyor; AI düğümü aynı koltuğa oturabilir, ama amaç aramayı ucuzlatıp spam'i artırmak değil, aramayı daha az ve daha iyi yapmak olmalı. Bunu teklif aramasından teslimata uzanan, iki AI düğümlü bir demo hikâyesine çevirdim ve Freya notuna ekledim.

---

### Kullanıcı · 14:51

safarideki speech to text daha iyi çalışıyodu ama sanki enn başta denediğimde, chromeda bağırmam gerekiyor ve bazen yanlış anlıyor. mimariden kaynaklanan bir şey mi bu?

### Claude

Önce koda bakıyorum: Chrome'da konuşma tanıma nasıl başlatılıyor, asistan konuşurken mikrofon ne zaman kapanıyor, cümlenin bittiğine nasıl karar veriliyor. Cevap bunlara bağlı.

**Kısmen evet.** Kodu okudum. Sorun üç katmandan geliyor: ikisi mimari, biri ortam.

## 1. STT'yi tarayıcıya bıraktık (mimari bir seçim)

`webkitSpeechRecognition` iki tarayıcıda farklı motorlara gidiyor:
- Chrome sesi Google'ın sunucusuna gönderiyor.
- Safari Apple'ın dikte servisini kullanıyor.

Mikrofon sesinin işlenmesi (otomatik kazanç, gürültü bastırma) de iki tarayıcıda farklı. Biz bunların hiçbirini ayarlayamıyoruz: model seçimi, kazanç, ilçe ve ay adları için kelime ipucu verme imkânı yok. Tarayıcıların arasındaki kalite farkı buradan geliyor. Senin denemene göre Türkçede ve senin mikrofonunda Apple'ın motoru daha iyi çalışıyor.

Bu bilinçli bir ödünleşimdi: Deepgram kullanılamıyordu, ücretsiz ve gerçek zamanlı çalışan en kısa yol buydu.

## 2. Asistan konuşurken mikrofon kapalı (bizim tasarımımız)

`app.js` asistan düşünürken ya da konuşurken tanımayı tamamen kapatıyor (`rec.abort()`). Asistan sustuktan sonra 600 ms bekliyor (`IDLE_MS`), sonra **sıfırdan yeni bir tanıma oturumu** açıyor. Chrome'un bu oturumu başlatıp mikrofonu açması da ayrıca zaman alıyor. Sonuç:

- **Asistan sustuğu anda cevap verirsen ilk kelimen kaçabiliyor.** "Evet, benim" yerine "benim", ya da cümlenin ortasından anlamsız bir parça gidiyor. "Yanlış anlıyor" hissinin bir kısmı buradan geliyor.
- **Kısa bir duraklama cümleni bölüyor.** 700 ms sessizlik olunca (`ENDPOINT_MS`) cümle bitmiş sayılıp gönderiliyor. Doğum tarihini "on dört… mart… seksen sekiz" diye söylersen parça parça gidebilir.
- **Bazen ara sonuç gönderiliyor.** Chrome kesin sonucu yaklaşık 1,25 saniye içinde vermezse kod ara sonucu (interim) gönderiyor, bu da daha hatalı bir metin.

Bu tasarımı, hoparlörden çıkan asistan sesi STT'ye girmesin diye seçtik. Yankı engelleme olmadığı için yapılabilecek en basit şey buydu.

## 3. "Bağırmam gerekiyor" büyük ihtimalle ortamdan

Bu belirtiye en çok uyan neden mimari değil. **Chrome kendi mikrofon seçimini tutuyor** ve bu seçim sistemin varsayılan mikrofonundan farklı olabilir. Örneğin monitörün ya da kameranın mikrofonu, iPhone mikrofonu, Zoom veya Teams'in sanal cihazı seçili olabilir.

Kontrol edilecek yerler:
- `chrome://settings/content/microphone` adresinde hangi mikrofonun seçili olduğu
- macOS'ta Sistem Ayarları → Ses → Giriş altındaki giriş seviyesi

Arayüzdeki çubuk gerçek bir ses seviyesi göstergesi değil. Yalnızca tanımanın olaylarını gösteriyor (mikrofon açık / ses var / konuşma var), o yüzden sesinin kısık geldiğini sana göstermiyor.

## Demo için kod değişikliği gerektirmeyen çözümler (2 saat doldu)

1. **Kulaklık tak ve "Söz kesme" kutusunu aç.** Kutu açıkken kod asistan konuşurken tanımayı kapatmıyor. Oturum hiç kapanmadığı için ilk kelimenin kaçma sorunu ortadan kalkıyor. Ama kayıt aracının sistem sesini de kaydettiğinden emin ol, yoksa videoda asistanın sesi duyulmaz.
2. Chrome'da doğru mikrofonu seç ve yakından konuş.
3. Asistan sustuktan sonra durum etiketinin "dinliyor" olmasını bekle, sonra konuş.
4. Doğum tarihi gibi bilgileri tek nefeste söyle.
5. Safari daha iyi anlıyorsa onu da kullanabilirsin. Ama daha önce yaşadığın mikrofon kesilmesi ve iznin tekrar sorulması riski devam ediyor. Kayıttan önce iki tarayıcıda da baştan sona bir arama yap, hangisi tam aramayı sorunsuz bitiriyorsa onu seç.

## Videoda söylenebilecek bulgu

Bu, "gerçek bankada neyi değiştirirdin?" sorusuna iyi bir cevap:
- Tarayıcı STT'si demo için yeterli. Gerçek bankada yankı engelleme olan, sunucu tarafında akan bir STT kullanırdın. Böylece mikrofon asistan konuşurken de açık kalır (tam çift yönlü).
- Bu STT ilçe ve ay adları için kelime ipuçlarını desteklemeli, telefon hattı sesine uygun bir modeli olmalı.
- Şu anki senaryo testi metin modunda çalışıyor, ses tanıma hatasını hiç ölçmüyor. STT hatası ayrıca ölçülmeli.

Bu bulguyu Freya notuna da ekledim.

result: Chrome'daki sorunun iki kısmı mimariden geliyor: STT tarayıcıya bırakıldığı için motor ve ses işleme ayarlanamıyor, ve asistan her konuştuğunda mikrofon kapanıp yeniden açıldığı için ilk kelime kaçabiliyor. "Bağırma" ihtiyacı ise büyük ihtimalle Chrome'un seçtiği mikrofondan; demo için kodsuz çözüm kulaklık takıp "Söz kesme"yi açmak ve Chrome'da doğru mikrofonu seçmek.

---

### Kullanıcı · 15:04

tamam görev 2 içinde bi şey oluştur

### Claude

Görev 2 için bir ürün tasarımı oluşturacağım. Bir uyarı: case "iki görev için toplam 2 saat, süre dolunca dur" diyor ve süre doldu. Yine de yapıyorum, ama videoda ve teslim mesajında bu tasarımın süre dolduktan sonra hazırlandığını açıkça söylemeni öneririm.

Konu olarak en güçlü aday dediğimiz C'yi seçiyorum: bankanın akış ve karar motoruna eklenen "AI görüşme düğümü", kart yaşam döngüsü hikâyesiyle. Görev 1 reposuna dokunmayacağım, ayrı bir klasörde tıklanabilir bir mock olacak. Önce sayfa yönergelerini yüklüyorum.

_(Kullanıcı Claude'u yarıda durdurdu.)_

---

### Kullanıcı · 15:15

ben senden görev 2 için yine bi artifact oluşturmanı istemiştim sadece

### Claude

Haklısın, gereğinden fazla planladım. Şimdi sade bir artifact yapıyorum: akış şeması, AI düğümü paneli, iki çalıştırma izi ve ürün notu. Dosyayı yazıp aynı adımda yayımlıyorum.

Yayımlandı. Son kontrol olarak sayfadaki script'in sözdizimini kontrol ediyorum ve Freya notuna Görev 2'nin nerede olduğunu ekliyorum.

Görev 2 artifact'ı hazır. Bekletmeyi de bu sefer gereksiz uzattım, kusura bakma.

**Link:** https://claude.ai/artifact/CoKTVZBkgyAg3jUoxRrtK6

Sayfada dört bölüm var:
- **Akış:** Kart yaşam döngüsü için 7 adımlık bir şerit: hedefleme, teklif araması (AI), yönlendirme, uygulamada onay, kurye, teslim araması (AI, yani Görev 1), istisna masası. Bir adıma tıklayınca altında ayarları açılıyor. Teklif araması düğümünde şunlar var: modele giden ve hiç gitmeyen bilgiler, araçlar, çıktı şeması, ve her kuralın nerede uygulandığını gösteren bir tablo.
- **Çalıştırma izi:** İki örnek görüşme. Birinde müşteri teklifi kabul ediyor. Diğerinde model "aidat yok" diyor, arama sonrası denetim bunu yakalıyor ve vaka istisna masasına düşüyor.
- **Ürün notu:** Görüşün, fikre adım adım nasıl vardığın, kimin için ve hangi işi gördüğü, bilerek dışarıda bıraktıkların, gerçek bankada açmadan önce yapılacaklar, nasıl ölçerdin.
- **Alt not:** Tasarımın 2 saatlik süre dolduktan sonra hazırlandığını söylüyor. İstersen kaldırırım, ama tutmanı öneririm.

Kontrol olarak sayfadaki script'in sözdizimini denetledim, sorun yok. Sayfayı tarayıcıda açıp görsel olarak kontrol etmedim.

Teslim için bilmen gerekenler:
- **Link şu an özel.** Değerlendiriciler açamaz; göndermeden önce sayfanın Share menüsünden paylaşıma açman gerekiyor.
- **Ya da dosyayı gönder:** Kaynak dosya `~/dev/personal/freya_fde_case/gorev2/gorusme-dugumu.html`, zip'e de koyabilirsin.

Değiştirmek istediğin bir yer olursa söyle, aynı linki güncellerim.

result: Görev 2 için "Görüşme Düğümü" ürün mock'u yayımlandı: https://claude.ai/artifact/CoKTVZBkgyAg3jUoxRrtK6 (kaynak: `~/dev/personal/freya_fde_case/gorev2/gorusme-dugumu.html`). Link özel; değerlendiricilere göndermeden önce Share menüsünden paylaşıma aç.
