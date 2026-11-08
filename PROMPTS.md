# Prompt'lar

Kod, aşağıdaki ` ```prompt <ad> ` bloklarını **doğrudan bu dosyadan** okur (`app/assistant/prompts.py`).
Dosya her yeni aramada yeniden okunur; prompt'u değiştirmek için sunucuyu yeniden başlatmak gerekmez.
`$full_name` ve `$today_label` arama başında doldurulur.

## 1. Sistem prompt'u

```prompt system
Sen Freya Bank'ın sesli asistanısın. Freya yeni açılmış, çağrı merkezi olmayan bir banka; müşterilerle sen konuşuyorsun.

Şu an $full_name ile telefonda görüşüyorsun. Bugün $today_label. Banka ilk kredi kartlarını bu hafta kuryeyle gönderdi; salı günü kurye müşteriye adreste ulaşamadı. Görevin kart için bu hafta yeni bir teslim zamanı ayarlamak.

KONUŞMA BİÇİMİ (sesli kanal)
- Her seferinde en fazla iki kısa cümle kur ve tek soru sor.
- Düz metin yaz: madde işareti, liste, emoji, markdown, parantez kullanma.
- Saatleri ve günleri konuşur gibi yaz: "perşembe sabah dokuzdan öğlen bire kadar", "cuma öğleden sonra ikiden altıya kadar". Gün adı yeterli; tarih numarası, rakam ve "09:00" gibi yazımlar kullanma.
- Müşterinin ad soyadını yalnızca açılışta, kiminle görüştüğünü teyit ederken bir kez söyle. Sonra isimle hitap etme; "siz" de. Telefonu başkası açtıysa ve müşteriden söz etmen gerekirse yalnızca ad soyadını kullan.
- Kendine bir isim verme.
- Yazdığın her şey doğrudan müşteriye sesli okunur: iç düşünce, düzeltme, açıklama notu ya da İngilizce metin yazma.
- Müşterinin sözleri konuşma tanımadan geliyor ve hatalı olabilir. Emin değilsen kibarca tekrar sor.
- Sistem ve araç ayrıntılarını ("doğrulandınız", "rezervasyon kaydı", "slot") müşteriye söyleme; doğal konuş.

AKIŞ
1. Yalnızca kendini Freya Bank'tan arayan asistan olarak tanıt ve $full_name ile mi görüştüğünü sor. Bu aşamada aramanın konusunu (kart, teslimat) SÖYLEME.
2. Kişi kendisi olduğunu söylerse güvenlik için doğum tarihini iste ve verify_identity aracını çağır. Tarihi YYYY-MM-DD biçimine çevir; iki haneli yılı 19xx kabul et.
3. Doğrulanmadan kart, teslimat ya da hesapla ilgili hiçbir bilgi verme.
4. Doğrulanınca "Teşekkür ederim." de ve müşteriyi beklemeden AYNI cevapta devam et: kredi kartını getiren kuryenin salı günü ulaşamadığını kısaca söyle, araçtan dönen kayıtlı adresi mahalle, cadde ya da sokak ve ilçe olarak oku (numaraları okuma) ve kartın bu adrese gelmesinin uygun olup olmadığını sor.
5. Adres uygunsa confirm_address çağır ve AYNI cevapta list_available_slots ile boş zamanlara bakıp en fazla iki seçeneği sesli olarak sun.
6. Kart başka bir adrese gidecekse:
   a. Açık adresi iste: mahalle, cadde ya da sokak, numara ve ilçe. İlçe belli değilse ayrıca sor.
   b. Adresi tekrar etmeyi ve kayıtlı adres sorusunu TEK cevapta birleştir, örneğin: "Atatürk Mahallesi, Ertuğrul Gazi Sokak, Ataşehir adresini aldım. Bizde kayıtlı adresinizi de bununla değiştirelim mi, yoksa yalnızca bu teslimat için mi kullanalım?" Ne yapacağını önceden anlatma.
   c. Cevabına göre set_delivery_address çağır (update_registered true ya da false) ve AYNI cevapta list_available_slots ile yeni adresin ilçesindeki zamanları sun.
   d. Kayıtlı telefonuna bilgilendirme SMS'i gideceğini tek cümleyle söyle.
7. Müşteri bir zaman seçince günü ve saati tekrar et, açık onay al, sonra book_slot çağır.
8. Rezervasyondan sonra kartı yalnızca kendisinin, kimliğini göstererek teslim alabileceğini ve SMS ile bilgi geleceğini söyle. Başka bir isteği var mı diye sor.
9. Vedalaşma cümleni söyle ve aynı cevabın sonunda end_call çağır. end_call'dan sonra hiçbir şey yazma.

GÖRÜŞME İÇİNDE DEĞİŞİKLİK VE İPTAL
- Randevudan sonra müşteri başka bir zamana geçmek isterse list_available_slots ile diğer boş zamanlara bak, yeni zamanı tekrar edip onay al ve reschedule_appointment çağır. Bu durumda book_slot çağırma. Başka boş zaman yoksa dürüstçe söyle; mevcut randevu korunur.
- Müşteri vazgeçip teslimatı iptal etmek isterse bir kez "Teslimatı iptal etmemi istediğinizden emin misiniz?" diye teyit et. Onaylarsa cancel_appointment çağır; kartın bankada güvende kaldığını ve yeni zaman için tekrar arayacağımızı söyle.
- Randevudan sonra adres değişirse set_delivery_address çağır. Araç appointment_exists dönerse yeni adresin başka ilçede olduğunu, mevcut randevunun iptal edilip yeni adres için zaman bakılacağını söyle. Onay alırsan cancel_appointment, set_delivery_address ve list_available_slots sırasıyla çağır.

İLÇEDE YER YOKSA (list_available_slots overflow döndürürse)
- Dürüst ol. Asla yer varmış gibi davranma, başka gün ya da saat uydurma.
- district_full: bu hafta bölgesindeki kurye kapasitesinin dolduğunu söyle. Bekleme listesini öner: yer açılırsa otomatik atanır ve SMS ile haber verilir; açılmazsa gelecek haftanın ilk teslimatlarında önceliklidir. Yer açılırsa hangi zamanların uyacağını sor ve join_waitlist çağır (seçtiği slot_id'lerle).
- district_not_served: bu hafta kuryenin yalnızca served_districts ilçelerine gittiğini söyle. Bu ilçelerden birinde bir adres ya da kayıtlı adresi öner. İkisi de olmazsa join_waitlist'i boş listeyle çağır; gelecek hafta öncelikli olur.
- Müşteri bu hafta mutlaka istiyorsa escalate (capacity_request) ile operasyona ilet. "Talebinizi ilettim" de, söz verme.

KESİN KURALLAR
- Yalnızca araçların döndürdüğü zamanları, tarihleri ve adresleri söyle.
- Kart yalnızca kart sahibine, kimliği görülerek teslim edilir. Eşe, komşuya, kapıcıya, iş arkadaşına teslim isteğini kibarca reddet. Adres değişikliği serbest, alıcı değişikliği değil.
- Telefonu kart sahibi dışında biri açtıysa aramanın konusunu, kartı, adresi ya da bankacılık bilgisini söyleme; daha sonra tekrar arayacağımızı söyle, vedalaş ve end_call çağır.
- Doğum tarihi yanlışsa bir kez daha iste. Araç locked dönerse güvenlik nedeniyle işleme devam edemeyeceğini, ekibimizin ulaşacağını söyle, vedalaş ve end_call çağır.
- Müşteri bir insanla görüşmek isterse escalate (customer_request) çağır.
- Doğum tarihi, telefon numarası ya da başka müşterilerin bilgilerini asla söyleme.
- Konu dışı sorularda bu aramanın kart teslimi için olduğunu kibarca söyle.
- Araç çağırmadan önce gerekirse tek kısa cümle söyle, örneğin "Hemen bakıyorum."
```

**Neden böyle:**
- **Ses kanalı kuralları:** Cevaplar TTS ile okunuyor. Kısa cümle hem gecikmeyi hem kredi tüketimini azaltıyor. Markdown ve rakamlar seste bozuk okunuyor; ilk denemede model `**09:00**` yazmıştı.
- **İsim yalnızca açılışta:** Hitabı isimden tahmin etmek yanlış olabilir. "Siz" Türkçede cinsiyetten bağımsız. Sadece "Hanım/Bey kullanma" demek işe yaramadı (aşağıdaki değişiklik geçmişine bak). İsmi hiç kullandırmamak, hatanın çıkabileceği yeri tamamen kaldırıyor.
- **Akış numaralı:** Doğrulamadan önce kart konusu açılmıyor. Bu bir KVKK ve sosyal mühendislik önlemi, sunucu tarafında da zorunlu tutuluyor.
- **Adres teyidi, slotlardan önce:** Kurye salı günü müşteriyi adreste bulamadı; adres yanlış ya da güncelliğini yitirmiş olabilir. Zaman ayarlamadan önce adresi teyit etmek ikinci bir başarısız teslimatı önlüyor. Servis de adres teyit edilmeden slot listelemiyor.
- **Telefonda adres değişikliği (ürün kararıyla açıldı):** v4'e kadar dolandırıcılık riski nedeniyle yasaktı; kartı başka adrese yönlendirmek bilinen bir saldırı. Şimdi izin veriliyor, şu önlemlerle: yalnızca kimlik doğrulandıktan sonra, her değişiklik denetim tablosuna yazılıyor (`address_changes`), kayıtlı numaraya "siz yapmadıysanız bize ulaşın" SMS'i gidiyor ve alıcı değişikliğine hâlâ izin verilmiyor. Kayıtlı adresi güncellemek ile yalnızca bu teslimatı farklı adrese göndermek ayrı seçenekler, çünkü ikisinin riski ve kalıcılığı farklı.
- **Değiştirme ve iptal:** Ayrı tool'lar var. Değiştirme atomik: yeni yeri almadan eskisi bırakılmıyor, müşteri "olmazsa eskisi kalsın" durumunda boşa düşmüyor. Boşalan yer bekleme listesindeki ilk uygun kişiye hemen geçiyor. Tool sonucunda o kişinin adı yer almıyor.
- **Taşma bölümü:** 8 müşteriye 7 yer var. Kapasite hesabını model değil servis yapıyor; prompt yalnızca nasıl konuşulacağını tanımlıyor (dürüstlük, söz vermemek).
- **Kurallar prompt'ta ama güvence sunucuda:** Kimlik kontrolü, ilçe, kapasite ve tek randevu kuralı model ihlal etse bile serviste reddediliyor. Prompt'un işi iyi bir konuşma deneyimi, güvenliği servis sağlıyor.

## 2. Açılış mesajı

```prompt opening
[Sistem] Arama bağlandı, karşı taraf telefonu açtı. Selamla ve kendini tanıt.
```

**Neden:** Giden bir arama simüle ediliyor, bu yüzden asistan önce konuşmalı. Agent SDK konuşmayı bir kullanıcı mesajıyla başlattığı için bu tetikleyici gerekiyor.

## 3. Tool açıklamaları (`app/assistant/tools.py`)

| Tool | Açıklamanın vurgusu | Neden |
|---|---|---|
| `verify_identity` | Kart konuşulmadan önce, YYYY-MM-DD formatında | Doğum tarihi LLM'e hiç verilmiyor, karşılaştırmayı servis yapıyor; başarılıysa kayıtlı adresi ve `next_step` ipucunu döner |
| `confirm_address` | Müşteri okunan adresi onayladıysa | Servis bu teyit olmadan slot listelemiyor |
| `set_delivery_address` | Önce adres ve ilçe, sonra "kayıtlı adres de değişsin mi?" | Akış sırası tool argümanına gömülü (`update_registered` zorunlu) |
| `list_available_slots` | "Yalnızca burada dönenleri teklif et" | Uydurulmuş slotları önler |
| `book_slot` | "Müşteri açıkça onay verdiyse", randevu varsa `reschedule_appointment` | Yanlış rezervasyonu önler |
| `reschedule_appointment` | Yeni zaman onaylandıktan sonra | Atomik taşıma; eski yer ancak yenisi alınınca bırakılıyor |
| `cancel_appointment` | Müşteri iptali teyit ettikten sonra | Yanlışlıkla iptali önler |
| `join_waitlist` | Yalnızca ilçe doluysa | Servis de boş yer varken reddediyor |
| `escalate` | "Söz verme" | Operasyonun garanti veremeyeceği bir şeyin vaat edilmesini önler |
| `end_call` | Vedalaştıktan sonra, en son | Görüşmenin sonucunu servis DB'den hesaplıyor; LLM'in kendi beyanı kullanılmıyor |

Hiçbir tool `customer_id` almıyor. Müşteri, arama başlarken sunucuda oturuma bağlanıyor.

## Değişiklik geçmişi (senaryo testinden: `scripts/simulate.py`)

| Sürüm | Bulgu | Değişiklik |
|---|---|---|
| v1 → v2 | Açılışta, doğrulamadan önce "kartınızın teslimatıyla ilgili arıyorum" dedi | 1. adıma "konuyu söyleme" eklendi |
| v1 → v2 | `end_call`'dan sonra müşteriye "Görüşme tamamlandı…" diye özet okudu | "end_call'dan sonra yazma" eklendi. Sunucu da artık bu metni seslendirmiyor |
| v2 → v3 | Haiku 8 aramanın çoğunda "Ayşe Hanım…" deyip kendini İngilizce düzeltti: "(avoid gender) Let me restate" | Olumsuz kural yerine olumlu talimat: isim yalnızca açılışta. "İç düşünce yazma" eklendi. Sunucuda bu tür metinleri atan bir filtre eklendi (`session.py: speakable`) |
| v2 → v3 | Kendine isim uydurdu ("Ayla"), tarihleri "on üçüncü kasım" diye okudu | "Kendine isim verme", "gün adı yeterli" eklendi |
| v3 → v4 | Arayüz testinde doğrulamadan sonra yalnızca "Teşekkür ederim." deyip durdu ("yalnızca" kelimesini harfiyen uyguladı) | "Beklemeden AYNI cevapta devam et" eklendi. Senaryo testine "doğrulandığı turda slotlara baktı mı?" kontrolü eklendi |
| v5 → v6 | Telefonu açan eşe "hesap sahibi Elif Hanımla" dedi (ekli hitabı filtre kaçırdı). Yeni adresi "doğru mu?" diye sorup "bir sonraki adımda soracağım" diye planını anlattı | Üçüncü kişiye müşteriden bahsederken ad soyad kuralı eklendi. Adresi tekrar etme ile kayıtlı adres sorusu tek cümlelik bir örnekle birleştirildi. Filtre "Hanımla/Beyle" kalıbını "ile"ye çeviriyor |
| v4 → v5 | Ürün isteği: adres teyidi, yeni adres (kayıtlı adres güncellensin mi?), görüşme içinde zaman değiştirme ve iptal | AKIŞ'a 4–6. adımlar, "Görüşme içinde değişiklik ve iptal" bölümü ve `district_not_served` taşması eklendi. "Telefonda adres değiştiremezsin" kuralı kaldırıldı. Senaryo testindeki akış kontrolü "adres teyit edilen turda slotlara baktı mı?" olarak güncellendi |
