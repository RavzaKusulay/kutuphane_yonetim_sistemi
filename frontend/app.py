import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://backend:8000")

st.set_page_config(page_title="Kutuphane Sistemi", layout="wide")

# --- OTURUM (SESSION) YONETIMI ---
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'role' not in st.session_state:
    st.session_state.role = None

st.title("Kutuphane Yonetim Sistemi")
st.markdown("Kutuphane veritabani ve kullanici arayuzune hos geldiniz.")

# --- SOL MENU (DINAMIK) ---
st.sidebar.title("Menu")
if st.session_state.token:
    st.sidebar.success(f"Hos geldin, {st.session_state.username}! ({st.session_state.role})")
    if st.sidebar.button("Cikis Yap"):
        for key in ['token', 'username', 'user_id', 'role']:
            st.session_state[key] = None
        st.rerun()
else:
    st.sidebar.warning("Lutfen islem yapabilmek icin giris yapin.")

# Rol bazli menu yonetimi
menu = ["Kitap Katalogu ve Arama", "Hesap Islemleri (Giris/Kayit)"]
if st.session_state.token:
    menu.extend(["Odunc, Iade ve Rezervasyon", "Islem Gecmisim"])
    if st.session_state.role in ["admin", "librarian"]:
        menu.extend(["Yonetici Paneli (Islemler)", "Yonetici Raporlari"])
menu.append("Sistem Durumu")

choice = st.sidebar.selectbox("Gideceginiz Sayfa", menu)

headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

# --- SAYFA 1: KITAP KATALOGU VE ARAMA ---
if choice == "Kitap Katalogu ve Arama":
    st.subheader("Mevcut Kitap Katalogu ve Arama")
    tab_all, tab_search = st.tabs(["Tum Kitaplar", "Kitap Ara"])
    
    with tab_all:
        try:
            res = requests.get(f"{API_URL}/books")
            if res.status_code == 200 and res.json():
                df = pd.DataFrame(res.json())
                df = df[['id', 'isbn', 'title', 'author', 'publisher', 'available_copies']]
                df.columns = ['Kitap ID', 'ISBN', 'Kitap Adi', 'Yazar', 'Yayinevi', 'Mevcut Stok']
                
                # YENI EKLENEN KISIM: Kitap ID'ye gore kucukten buyuge sirala ve indeksi sifirla
                df = df.sort_values(by='Kitap ID', ascending=True).reset_index(drop=True)
                
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Kutuphanede henuz kitap bulunmuyor.")
        except:
            st.error("Backend servisine baglanilamadi.")
            
    with tab_search:
        search_query = st.text_input("Aramak istediginiz kelimeyi girin (Baslik, Yazar, Yayin Evi veya ISBN):")
        if st.button("Ara"):
            if search_query:
                try:
                    res = requests.get(f"{API_URL}/books/search?keyword={search_query}")
                    if res.status_code == 200 and res.json():
                        df = pd.DataFrame(res.json())
                        df = df[['id', 'isbn', 'title', 'author', 'publisher', 'available_copies']]
                        df.columns = ['Kitap ID', 'ISBN', 'Kitap Adi', 'Yazar', 'Yayinevi', 'Mevcut Stok']
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("Aradiginiz kritere uygun kitap bulunamadi.")
                except:
                    st.error("Arama yapilamadi veya arka plan sunucusuna ulasilamadi.")

# --- SAYFA 2: HESAP ISLEMLERI ---
elif choice == "Hesap Islemleri (Giris/Kayit)":
    st.subheader("Kullanici Islemleri")
    if st.session_state.token:
        st.info("Su anda sisteme giris yapmis durumdasiniz.")
    else:
        tab1, tab2 = st.tabs(["Giris Yap", "Kayit Ol"])
        with tab1:
            with st.form("login_form"):
                login_email = st.text_input("E-posta Adresi")
                login_password = st.text_input("Sifre", type="password")
                if st.form_submit_button("Giris Yap"):
                    try:
                        res = requests.post(f"{API_URL}/login", json={"email": login_email, "password": login_password})
                        if res.status_code == 200:
                            acc_token = res.json().get("access_token")
                            user_res = requests.get(f"{API_URL}/me", headers={"Authorization": f"Bearer {acc_token}"})
                            if user_res.status_code == 200:
                                u_data = user_res.json()
                                st.session_state.token = acc_token
                                st.session_state.username = u_data.get("username")
                                st.session_state.user_id = u_data.get("id")
                                st.session_state.role = u_data.get("role")
                                st.success("Giris basarili! Yonlendiriliyorsunuz...")
                                st.rerun()
                        else:
                            st.error("E-posta veya sifre hatali.")
                    except requests.exceptions.RequestException:
                        st.error("Backend servisine ulasilamiyor.")
                        
        with tab2:
            with st.form("register_form"):
                reg_username = st.text_input("Kullanici Adi")
                reg_email = st.text_input("E-posta Adresi")
                reg_password = st.text_input("Sifre", type="password")
                if st.form_submit_button("Kayit Ol"):
                    try:
                        res = requests.post(f"{API_URL}/register", json={"username": reg_username, "email": reg_email, "password": reg_password})
                        if res.status_code == 200:
                            st.success("Kayit basarili! Lutfen Giris Yap sekmesinden giris yapiniz.")
                        else:
                            st.error("Kayit basarisiz. E-posta kullanimda olabilir.")
                    except requests.exceptions.RequestException:
                        st.error("Backend hatasi.")

# --- SAYFA 3: ODUNC, IADE VE REZERVASYON ---
elif choice == "Odunc, Iade ve Rezervasyon":
    st.subheader("Kitap Islemleri")
    tab_borrow, tab_return, tab_reserve = st.tabs(["Odunc Al", "Iade Et", "Rezervasyon Yap"])
    
    with tab_borrow:
        with st.form("borrow_form"):
            b_id = st.number_input("Odunc Alinacak Kitap ID", min_value=1, step=1)
            if st.form_submit_button("Odunc Al"):
                res = requests.post(f"{API_URL}/borrow", json={"book_id": b_id, "user_id": st.session_state.user_id}, headers=headers)
                if res.status_code == 200: st.success("Kitap odunc alindi!")
                else: st.error(res.json().get('detail'))
                    
    with tab_return:
        with st.form("return_form"):
            r_id = st.number_input("Iade Edilecek Kitap ID", min_value=1, step=1)
            if st.form_submit_button("Iade Et"):
                res = requests.post(f"{API_URL}/return", json={"book_id": r_id, "user_id": st.session_state.user_id}, headers=headers)
                if res.status_code == 200: st.success("Kitap iade edildi!")
                else: st.error(res.json().get('detail'))
                    
    with tab_reserve:
        with st.form("reserve_form"):
            res_id = st.number_input("Rezerve Edilecek Kitap ID", min_value=1, step=1)
            if st.form_submit_button("Rezervasyon Yap"):
                res = requests.post(f"{API_URL}/reserve", json={"book_id": res_id, "user_id": st.session_state.user_id}, headers=headers)
                if res.status_code == 200: st.success("Rezervasyon basarili!")
                else: st.error(res.json().get('detail'))

# --- SAYFA 4: ISLEM GECMISIM ---
elif choice == "Islem Gecmisim":
    st.subheader("Odunc Alma Gecmisiniz")
    res = requests.get(f"{API_URL}/history/{st.session_state.user_id}", headers=headers)
    if res.status_code == 200 and res.json():
        df = pd.DataFrame(res.json())
        df = df[['book_id', 'borrow_date', 'due_date', 'return_date', 'status']]
        df.columns = ['Kitap ID', 'Alis Tarihi', 'Son Teslim Tarihi', 'Iade Tarihi', 'Durum']
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Henuz bir islem gecmisiniz bulunmuyor.")

# --- SAYFA 5: YONETICI PANELI (ISLEMLER) ---
elif choice == "Yonetici Paneli (Islemler)":
    st.subheader("Kitap ve Kullanici Yonetimi")
    t_add, t_upd, t_del, t_usr, t_usr_del = st.tabs(["Kitap Ekle", "Kitap Guncelle", "Kitap Sil", "Tum Kullanicilar", "Kullanici Sil"])
    
    with t_add:
        with st.form("add_book_form"):
            isbn = st.text_input("ISBN Numarasi")
            title = st.text_input("Kitap Adi")
            author = st.text_input("Yazar")
            publisher = st.text_input("Yayin Evi")
            year = st.number_input("Yayin Yili", min_value=0, max_value=2100, step=1)
            copies = st.number_input("Kopya Sayisi", min_value=1, step=1)
            if st.form_submit_button("Sisteme Ekle"):
                b_data = {"isbn": isbn, "title": title, "author": author, "publisher": publisher, "publish_year": year, "total_copies": copies}
                res = requests.post(f"{API_URL}/books", json=b_data, headers=headers)
                if res.status_code == 200: st.success("Kitap basariyla eklendi!")
                else: st.error("Ekleme basarisiz. (Mevcut ISBN numarasina veya hatali veriye sahip olabilirsiniz)")
                    
    with t_upd:
        with st.form("update_book_form"):
            u_id = st.number_input("Guncellenecek Kitap ID Numarasi", min_value=1, step=1)
            u_isbn = st.text_input("Yeni ISBN Numarasi")
            u_title = st.text_input("Yeni Kitap Adi")
            u_author = st.text_input("Yeni Yazar Adi")
            u_pub = st.text_input("Yeni Yayin Evi")
            u_year = st.number_input("Yeni Yayin Yili", min_value=0, step=1)
            u_cop = st.number_input("Yeni Kopya Sayisi", min_value=1, step=1)
            if st.form_submit_button("Kitabi Guncelle"):
                ub_data = {"isbn": u_isbn, "title": u_title, "author": u_author, "publisher": u_pub, "publish_year": u_year, "total_copies": u_cop}
                res = requests.put(f"{API_URL}/books/{u_id}", json=ub_data, headers=headers)
                if res.status_code == 200: st.success("Kitap basariyla guncellendi!")
                else: st.error("Guncelleme basarisiz. (Lutfen kitabin ID numarasini kontrol edin)")
                    
    with t_del:
        with st.form("delete_book_form"):
            d_id = st.number_input("Sistemden Tamamen Silinecek Kitap ID Numarasi", min_value=1, step=1)
            if st.form_submit_button("Sistemden Kalici Olarak Sil"):
                res = requests.delete(f"{API_URL}/books/{d_id}", headers=headers)
                if res.status_code == 200: st.success("Kitap sistemden basariyla silindi!")
                else: st.error("Kitap bulunamadi veya sistem tarafindan silinemedi.")
                    
    with t_usr:
        st.write("Sistemde kayitli tum kullanicilari gormek icin butona basin.")
        if st.button("Kullanici Listesini Getir"):
            res = requests.get(f"{API_URL}/users", headers=headers)
            if res.status_code == 200 and res.json():
                df = pd.DataFrame(res.json())
                df = df[['id', 'username', 'email', 'role', 'created_at']]
                df.columns = ['ID Numarasi', 'Kullanici Adi', 'E-posta Adresi', 'Sistem Rolu', 'Kayit Olma Tarihi']
                st.dataframe(df, use_container_width=True)
                
    with t_usr_del:
        with st.form("delete_user_form"):
            del_u_id = st.number_input("Silinecek Kullanici ID Numarasi", min_value=1, step=1)
            if st.form_submit_button("Kullaniciyi Sistemden Kalici Olarak Sil"):
                res = requests.delete(f"{API_URL}/users/{del_u_id}", headers=headers)
                if res.status_code == 200: 
                    st.success("Kullanici sistemden basariyla silindi!")
                else: 
                    st.error("Kullanici bulunamadi veya silinemedi.")

# --- SAYFA 6: YONETICI RAPORLARI ---
elif choice == "Yonetici Raporlari":
    st.subheader("Sistem Raporlari ve Istatistikler")
    t_rep1, t_rep2, t_rep3, t_rep4, t_rep5 = st.tabs(["Gecikmis Kitaplar", "Aktif Odunc Durumu", "En Cok Okunanlar", "Aylik Istatistikler", "Ham Odunc Listesi"])
    
    with t_rep1:
        res = requests.get(f"{API_URL}/reports/overdue", headers=headers)
        if res.status_code == 200 and res.json(): st.dataframe(pd.DataFrame(res.json()), use_container_width=True)
        else: st.success("Sistemde su an gecikmis kitap bulunmamaktadir.")
            
    with t_rep2:
        res = requests.get(f"{API_URL}/reports/active-users", headers=headers)
        if res.status_code == 200 and res.json(): st.dataframe(pd.DataFrame(res.json()), use_container_width=True)
        else: st.info("Sistemde uzerinde aktif olarak kitap bulunan kullanici bulunmamaktadir.")
            
    with t_rep3:
        res = requests.get(f"{API_URL}/reports/most-borrowed", headers=headers)
        if res.status_code == 200 and res.json(): 
            df = pd.DataFrame(res.json())
            
            # YENI EKLENEN KISIM: Odunc Alinma Sayisina gore buyukten kucuge sirala
            df = df.sort_values(by='Odunc Alinma Sayisi', ascending=False).reset_index(drop=True)
            
            st.dataframe(df, use_container_width=True)
        else: 
            st.info("Sistemde gosterilecek kadar veri bulunmamaktadir.")
            
    with t_rep4:
        res = requests.get(f"{API_URL}/reports/monthly-stats", headers=headers)
        if res.status_code == 200 and res.json(): st.dataframe(pd.DataFrame(res.json()), use_container_width=True)
        else: st.info("Sistemde gosterilecek kadar veri bulunmamaktadir.")
            
    with t_rep5:
        st.write("Veritabaninda bekleyen butun islem goren ve iade edilmemis kitaplarin ham verileri asagidadir.")
        res = requests.get(f"{API_URL}/reports/currently-borrowed", headers=headers)
        if res.status_code == 200 and res.json(): st.dataframe(pd.DataFrame(res.json()), use_container_width=True)
        else: st.info("Mevcut durumda odunc alinmis veya bekleyen islem bulunmamaktadir.")

# --- SAYFA 7: SISTEM DURUMU ---
elif choice == "Sistem Durumu":
    st.subheader("API ve Veritabani Baglantisi Kontrolu")
    try:
        if requests.get(f"{API_URL}/").status_code == 200: st.success("Arka Plan (Backend) Servisi Aktif ve Sorunsuz Olarak Calismaktadir.")
    except: st.error("Baglanti Hatasi: Arka plan servisine ulasilamiyor.")