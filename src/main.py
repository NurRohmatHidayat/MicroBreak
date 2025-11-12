import cv2
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# ===============================
# KONFIGURASI RESOLUSI
# ===============================
RESOLUSI = {
    "120p": (160, 120),
    "240p": (320, 240),
    "360p": (480, 360),
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080)
}


# ===============================
# FUNGSI DETEKSI WAJAH
# ===============================
def load_cascade():
    path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(path)
    if face_cascade.empty():
        raise RuntimeError("Gagal memuat Haar Cascade.")
    return face_cascade


def detect_and_draw(frame, face_cascade, scaleFactor, minNeighbors):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=scaleFactor,
        minNeighbors=minNeighbors,
        minSize=(30, 30)
    )
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return frame, faces


# ===============================
# KELAS UTAMA GUI
# ===============================
class FaceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("👁️ Face Detection Timer")
        self.geometry("420x520")
        self.configure(bg="#f8f9fa")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 11), padding=6, relief="flat")
        self.style.configure("TLabel", background="#f8f9fa", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), background="#f8f9fa", foreground="#0078D7")

        self.running = False
        self.thread = None

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Face Detection & Timer", style="Title.TLabel").pack(pady=15)
        form = ttk.Frame(self)
        form.pack(pady=10)


        # Frame form
        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="Resolusi:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.res_var = tk.StringVar(value="480p")
        ttk.Combobox(form, textvariable=self.res_var, values=list(RESOLUSI.keys()), width=10).grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Scale Factor:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.scale_var = tk.DoubleVar(value=1.1)
        ttk.Entry(form, textvariable=self.scale_var, width=10).grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Min Neighbors:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.neighbor_var = tk.IntVar(value=5)
        ttk.Entry(form, textvariable=self.neighbor_var, width=10).grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Kamera Index:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.cam_var = tk.IntVar(value=0)
        ttk.Entry(form, textvariable=self.cam_var, width=10).grid(row=3, column=1, pady=5)

        ttk.Label(form, text="Micro Break (detik):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.micro_var = tk.DoubleVar(value=10.0)
        ttk.Entry(form, textvariable=self.micro_var, width=10).grid(row=4, column=1, pady=5)

        # Frame tombol
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)

        self.start_btn = ttk.Button(btn_frame, text="▶ Mulai Deteksi", command=self.start_thread)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="⏹ Hentikan", command=self.stop_detection, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=5)

        self.close_btn = ttk.Button(btn_frame, text="❌ Tutup GUI", command=self.close_app)
        self.close_btn.grid(row=0, column=2, padx=5)

        # Log status
        ttk.Label(self, text="Status Program:").pack(pady=(10, 0))
        self.log_box = tk.Text(self, height=8, width=46, bg="#ffffff", fg="#333333", relief="solid", wrap="word")
        self.log_box.pack(pady=5)
        self.log_box.insert("end", "Menunggu deteksi dimulai...\n")
        self.log_box.configure(state="disabled")

        ttk.Label(self, text="© PENS - Face Detection GUI", foreground="#777777", font=("Segoe UI", 9)).pack(side="bottom", pady=5)

    def log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def start_thread(self):
        if not self.running:
            self.running = True
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            # self.thread = threading.Thread(target=self.run_detection)
            self.thread = threading.Thread(target=self.run_detection, daemon=True)
            self.thread.start()

    def stop_detection(self):
        self.running = False
        cv2.destroyAllWindows()  # tutup jendela OpenCV
        self.start_btn.configure(state="normal")
        self.log("[INFO] Deteksi dihentikan oleh pengguna.")

    def close_app(self):
        """Hentikan deteksi dan tutup GUI"""
        if self.running:
            self.stop_detection()  # hentikan thread dan tutup kamera
        self.destroy()  # tutup jendela Tkinter


    def run_detection(self):
        try:
            res = self.res_var.get()
            width, height = RESOLUSI[res]
            face_cascade = load_cascade()

            cap = cv2.VideoCapture(int(self.cam_var.get()))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            self.log(f"[INFO] Kamera dibuka {width}x{height}")
            self.log("[INFO] Kamu bisa ubah parameter (scaleFactor, minNeighbors, Micro Break) saat deteksi berjalan.")

            start_time = None
            total_time = 0
            last_seen_time = None
            is_present = False

            # Variabel FPS
            prev_time = time.time()
            fps = 0

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    self.log("[ERROR] Tidak dapat membaca frame dari kamera.")
                    break

                # Hitung FPS
                current_time = time.time()
                dt = current_time - prev_time
                if dt > 0:
                    fps = 1.0 / dt
                prev_time = current_time

                # 🔄 Ambil nilai parameter terbaru dari GUI
                scale_factor = self.scale_var.get()
                min_neighbors = self.neighbor_var.get()
                micro_break = self.micro_var.get()

                frame, faces = detect_and_draw(frame, face_cascade, scale_factor, min_neighbors)
                current_time = time.time()

                if len(faces) > 0:
                    if not is_present:
                        if last_seen_time is not None:
                            gap = current_time - last_seen_time
                            if gap <= micro_break:
                                self.log(f"[INFO] Micro break: {gap:.1f}s, lanjut hitung.")
                            else:
                                self.log(f"[INFO] Orang kembali setelah {gap:.1f}s (reset timer).")
                                total_time = 0
                                start_time = current_time
                        else:
                            start_time = current_time
                        is_present = True

                    total_time = current_time - start_time
                    last_seen_time = current_time
                    status = "DI DEPAN KAMERA"

                else:
                    if is_present:
                        last_seen_time = current_time
                        is_present = False
                    else:
                        if last_seen_time is not None:
                            if current_time - last_seen_time > micro_break:
                                status = "TERLALU LAMA TIDAK DI DEPAN KAMERA"
                            else:
                                status = f"MICRO BREAK ({current_time - last_seen_time:.1f}s)"
                        else:
                            status = "MENUNGGU DETEKSI WAJAH"

                cv2.putText(frame, f"Status: {status}", (10, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)

                # Konversi total_time ke jam:menit:detik
                hours = int(total_time // 3600)
                minutes = int((total_time % 3600) // 60)
                seconds = int(total_time % 60)
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                cv2.putText(frame, f"Total waktu: {time_str}", (10, 55),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                cv2.putText(frame, f"FPS: {fps:.1f}", (width - 150, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                cv2.imshow("Face Detection Timer", frame)

                key = cv2.waitKey(1) & 0xFF
                if key in (ord('q'), 27):
                    break

            cap.release()
            cv2.destroyAllWindows()
            self.running = False
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.log("[INFO] Kamera ditutup.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"[ERROR] {e}")


if __name__ == "__main__":
    app = FaceApp()
    app.mainloop()