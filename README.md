# Kütüphane Yönetim Sistemi

## Proje Hakkında

Bu proje, dijital ortamda bir kütüphane sisteminin yönetilmesini sağlayan backend tabanlı bir uygulamadır.

Sistem; kullanıcı kayıt işlemleri, kullanıcı giriş sistemi, kitap ekleme/güncelleme/silme işlemleri, kitap ödünç alma ve iade süreçleri, rezervasyon oluşturma ve raporlama işlemlerini desteklemektedir.

Proje kapsamında gerçek bir veri seti kullanılarak başlangıç kitap envanteri oluşturulmuş ve veriler veritabanına aktarılmıştır.

Bu proje, IYD 328 İş Yeri Deneyimi dersi kapsamında geliştirilmiştir.

---

## Kullanılan Teknolojiler

Projede kullanılan teknolojiler:

* Python 3
* FastAPI
* PostgreSQL
* SQLAlchemy ORM
* Docker
* Pandas
* JWT (JSON Web Token)
* Swagger API Dokümantasyonu

---

## Veri Seti

Proje başlangıç kitap envanteri olarak Kaggle üzerinde bulunan Books Dataset veri setini kullanmaktadır.

Veri setinde aşağıdaki bilgiler bulunmaktadır:

* ISBN
* Kitap Adı
* Yazar
* Yayınevi
* Yayın Yılı

Veri seti temizlenmiş ve Python scripti kullanılarak PostgreSQL veritabanına aktarılmıştır.

---

## Sistem Özellikleri

### Kullanıcı Yönetimi

Sistem aşağıdaki kullanıcı işlemlerini destekler:

* Kullanıcı kayıt oluşturma
* Kullanıcı giriş işlemi
* Şifrelerin hashlenerek güvenli şekilde saklanması
* JWT token oluşturulması

---

### Kitap Yönetimi

Sistem üzerinde kitaplarla ilgili şu işlemler yapılabilir:

* Yeni kitap ekleme
* Kitap bilgilerini güncelleme
* Kitap silme
* Kitap arama
* Tüm kitapları listeleme

---

### Ödünç Alma Sistemi

Sistem aşağıdaki işlemleri destekler:

* Kitap ödünç alma
* Son teslim tarihi oluşturma
* Kitabın uygunluk durumunu kontrol etme
* Ödünç alınan kitabın stok bilgisini güncelleme

---

### Kitap İade Sistemi

Kullanıcılar ödünç aldıkları kitapları iade edebilir.

İade sırasında:

* İşlem durumu güncellenir
* İade tarihi kaydedilir
* Kitap stok sayısı artırılır

---

### Rezervasyon Sistemi

Eğer kitap mevcut değilse kullanıcı rezervasyon oluşturabilir.

Sistem:

* Kitap mevcut değilse rezervasyon oluşturur
* Aynı kullanıcının aynı kitap için birden fazla rezervasyon oluşturmasını engeller

---

### Raporlama Sistemi

Sistem aşağıdaki raporları üretmektedir:

* En çok ödünç alınan kitaplar
* Gecikmiş kitaplar
* Kullanıcının ödünç alma geçmişi

---

## Veritabanı Tasarımı

Projede PostgreSQL veritabanı kullanılmaktadır.

Oluşturulan temel tablolar:

### Users

Kullanıcı bilgilerini saklar.

Alanlar:

* id
* username
* email
* password_hash
* role
* created_at

---

### Books

Kitap bilgilerini saklar.

Alanlar:

* id
* isbn
* title
* author
* publisher
* publish_year
* total_copies
* available_copies

---

### Borrow Transactions

Ödünç alma işlemlerini saklar.

Alanlar:

* id
* user_id
* book_id
* borrow_date
* due_date
* return_date
* status

---

### Reservations

Rezervasyon bilgilerini saklar.

Alanlar:

* id
* user_id
* book_id
* reservation_date
* status

---

## API Endpointleri

### Kullanıcı İşlemleri

```text
POST /register
POST /login
```

---

### Kitap İşlemleri

```text
POST /books
GET /books
PUT /books/{id}
DELETE /books/{id}
GET /books/search
```

---

### Ödünç Alma İşlemleri

```text
POST /borrow
POST /return
GET /history/{user_id}
```

---

### Rezervasyon İşlemleri

```text
POST /reserve
```

---

### Raporlama

```text
GET /reports/most-borrowed
GET /reports/overdue
```

---

## Projenin Çalıştırılması

Projeyi klonlayın:

```bash
git clone <repository-url>
```

Sanal ortam oluşturun:

```bash
python -m venv venv
```

Sanal ortamı aktif edin:

```bash
venv\Scripts\activate
```

Gerekli paketleri kurun:

```bash
pip install -r requirements.txt
```

Docker containerını çalıştırın:

```bash
docker compose up -d
```

Uygulamayı başlatın:

```bash
uvicorn app.main:app --reload
```

---

## API Dokümantasyonu

Swagger arayüzü üzerinden endpointler test edilebilir.

Adres:

```text
http://127.0.0.1:8000/docs
```

---

## Proje Klasör Yapısı

```text
kutuphane_yonetim_sistemi/

app/
 ├── api/
 ├── auth/
 ├── database/
 ├── models/
 ├── schemas/

books_data/

scripts/
tests/

.gitignore
Dockerfile
docker-compose.yml
README.md
requirements.txt
```

---

## Gelecekte Yapılabilecek Geliştirmeler

İlerleyen süreçte sisteme şu özellikler eklenebilir:

* Frontend arayüz geliştirilmesi
* Rol bazlı yetkilendirme sistemi
* Gelişmiş filtreleme seçenekleri
* Sayfalama (pagination) desteği
* Email bildirim sistemi
* Yönetici paneli
* Unit test yapısı

---

## Proje Sahibi

Bu proje, backend geliştirme, veritabanı yönetimi ve API tasarımı konularında pratik kazanmak amacıyla geliştirilmiştir.
