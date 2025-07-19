// Veri yönetimi (IndexedDB için geliştirilmiş)
let studyData = {};
let timerRunning = false;
let startTime = null;
let elapsedTime = 0;
let timerInterval = null;

// Local Storage ile veri yönetimi
function loadData() {
    try {
        const data = localStorage.getItem('studyData');
        studyData = data ? JSON.parse(data) : {};
    } catch (error) {
        console.error('Veri yüklenirken hata:', error);
        studyData = {};
    }
}

function saveData() {
    try {
        localStorage.setItem('studyData', JSON.stringify(studyData));
    } catch (error) {
        console.error('Veri kaydedilirken hata:', error);
    }
}

// Bugünün tarih anahtarı
function getTodayKey() {
    return new Date().toISOString().split('T')[0];
}

// Bugünün verilerini getir/oluştur
function getTodayData() {
    const today = getTodayKey();
    if (!studyData[today]) {
        studyData[today] = {
            questions: {
                "Matematik": {correct: 0, wrong: 0},
                "Türkçe": {correct: 0, wrong: 0},
                "Fen": {correct: 0, wrong: 0},
                "Sosyal": {correct: 0, wrong: 0},
                "İngilizce": {correct: 0, wrong: 0},
                "Diğer": {correct: 0, wrong: 0}
            },
            pages_read: 0,
            notes_written: 0,
            study_time: 0,
            empty_day: true
        };
    }
    return studyData[today];
}

// Saat güncellemesi
function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('tr-TR');
    const dateStr = now.toLocaleDateString('tr-TR', {
        weekday: 'long',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });

    document.getElementById('clock').textContent = timeStr;
    document.getElementById('date').textContent = dateStr;
}

// Timer başlat
function startTimer() {
    hapticFeedback();
    if (!timerRunning) {
        timerRunning = true;
        startTime = Date.now();

        const startTimeStr = new Date().toLocaleTimeString('tr-TR', {hour: '2-digit', minute: '2-digit'});
        document.getElementById('startTime').textContent = `Başlangıç: ${startTimeStr}`;

        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;

        timerInterval = setInterval(updateTimer, 1000);

        // Wake Lock API (Ekranın kapanmasını engelle)
        if ('wakeLock' in navigator) {
            navigator.wakeLock.request('screen').catch(err => console.log(err));
        }
    }
}

// Timer durdur
function stopTimer() {
    hapticFeedback();
    if (timerRunning) {
        timerRunning = false;
        if (startTime) {
            elapsedTime += Date.now() - startTime;
            const todayData = getTodayData();
            todayData.study_time = Math.floor(elapsedTime / 1000);
            todayData.empty_day = false;
            saveData();
        }

        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('startTime').textContent = 'Başlangıç: --:--';

        if (timerInterval) {
            clearInterval(timerInterval);
        }

        updateDisplay();
    }
}

// Timer güncelle
function updateTimer() {
    if (timerRunning && startTime) {
        const currentTime = Math.floor((elapsedTime + (Date.now() - startTime)) / 1000);
        const hours = Math.floor(currentTime / 3600);
        const minutes = Math.floor((currentTime % 3600) / 60);
        const seconds = currentTime % 60;

        const timeStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        document.getElementById('timer').textContent = timeStr;
    }
}

// Soru ekle
function addQuestions() {
    hapticFeedback();
    const subject = document.getElementById('subject').value;
    const correct = parseInt(document.getElementById('correct').value) || 0;
    const wrong = parseInt(document.getElementById('wrong').value) || 0;

    if (correct < 0 || wrong < 0) {
        alert('Negatif sayı girilemez!');
        return;
    }

    const todayData = getTodayData();
    todayData.questions[subject].correct += correct;
    todayData.questions[subject].wrong += wrong;

    if (correct > 0 || wrong > 0) {
        todayData.empty_day = false;
    }

    saveData();
    updateDisplay();

    document.getElementById('correct').value = '0';
    document.getElementById('wrong').value = '0';

    // iOS Notification
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Soru Eklendi!', {
            body: `${subject} dersine ${correct} doğru, ${wrong} yanlış eklendi!`,
            icon: 'icon-192.png'
        });
    } else {
        alert(`${subject} dersine ${correct} doğru, ${wrong} yanlış eklendi!`);
    }
}

// Sayfa ekle
function addPages() {
    hapticFeedback();
    const pages = parseInt(document.getElementById('pages').value) || 0;

    if (pages < 0) {
        alert('Negatif sayı girilemez!');
        return;
    }

    const todayData = getTodayData();
    todayData.pages_read += pages;

    if (pages > 0) {
        todayData.empty_day = false;
    }

    saveData();
    updateDisplay();
    document.getElementById('pages').value = '0';

    alert(`${pages} sayfa eklendi!`);
}

// Not ekle
function addNotes() {
    hapticFeedback();
    const notes = parseInt(document.getElementById('notes').value) || 0;

    if (notes < 0) {
        alert('Negatif sayı girilemez!');
        return;
    }

    const todayData = getTodayData();
    todayData.notes_written += notes;

    if (notes > 0) {
        todayData.empty_day = false;
    }

    saveData();
    updateDisplay();
    document.getElementById('notes').value = '0';

    alert(`${notes} sayfa not eklendi!`);
}

// Ekranı güncelle
function updateDisplay() {
    const todayData = getTodayData();
    const today = new Date().toLocaleDateString('tr-TR');

    // Özet metni başlangıcı
    let summary = `📅 Bugün: ${today}\n\n`;

    // Toplam soru istatistikleri
    let totalCorrectQuestions = 0;
    let totalWrongQuestions = 0;
    let totalQuestionsAnswered = 0;

    summary += "📚 Çözülen Sorular:\n";
    for (const subject in todayData.questions) {
        const q = todayData.questions[subject];
        if (q.correct > 0 || q.wrong > 0) {
            summary += `- ${subject}: ${q.correct} Doğru, ${q.wrong} Yanlış\n`;
            totalCorrectQuestions += q.correct;
            totalWrongQuestions += q.wrong;
            totalQuestionsAnswered += q.correct + q.wrong;
        }
    }
    if (totalQuestionsAnswered === 0) {
        summary += "- Henüz soru çözülmedi.\n";
    }

    summary += `\n📖 Okunan Sayfa: ${todayData.pages_read} sayfa\n`;
    summary += `📝 Yazılan Not: ${todayData.notes_written} sayfa\n`;

    // Çalışma süresi formatlama
    const totalStudySeconds = todayData.study_time;
    const hours = Math.floor(totalStudySeconds / 3600);
    const minutes = Math.floor((totalStudySeconds % 3600) / 60);
    const seconds = totalStudySeconds % 60;
    const formattedStudyTime = `${hours}s ${minutes}d ${seconds}sn`; // Saat, Dakika, Saniye

    summary += `⏱️ Çalışma Süresi: ${formattedStudyTime}\n`;

    document.getElementById('summary').textContent = summary;

    // İstatistik kartlarını güncelle
    document.getElementById('totalQuestions').textContent = totalQuestionsAnswered;

    let accuracy = 0;
    if (totalQuestionsAnswered > 0) {
        accuracy = ((totalCorrectQuestions / totalQuestionsAnswered) * 100).toFixed(1);
    }
    document.getElementById('accuracy').textContent = `${accuracy}%`;

    document.getElementById('totalPages').textContent = todayData.pages_read;
    document.getElementById('totalTime').textContent = `${hours}s ${minutes}d`; // Sadece saat ve dakika gösterimi

    // Timer ekranını güncelle (eğer aktif değilse)
    if (!timerRunning) {
        document.getElementById('timer').textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

// Haftalık rapor gösterme (taslak)
function showWeeklyReport() {
    hapticFeedback();
    let report = "📚 Haftalık Çalışma Raporu:\n\n";
    let weeklyTotalQuestions = 0;
    let weeklyTotalCorrect = 0;
    let weeklyTotalWrong = 0;
    let weeklyTotalPages = 0;
    let weeklyTotalNotes = 0;
    let weeklyTotalStudyTime = 0; // in seconds

    const today = new Date();
    // Get the date 7 days ago
    for (let i = 0; i < 7; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const dayKey = date.toISOString().split('T')[0];
        const dayData = studyData[dayKey];

        if (dayData && !dayData.empty_day) {
            report += `--- ${date.toLocaleDateString('tr-TR', {weekday: 'short', month: '2-digit', day: '2-digit'})} ---\n`;
            let dayTotalQuestions = 0;
            let dayTotalCorrect = 0;
            let dayTotalWrong = 0;

            for (const subject in dayData.questions) {
                const q = dayData.questions[subject];
                if (q.correct > 0 || q.wrong > 0) {
                    report += `  - ${subject}: ${q.correct} D, ${q.wrong} Y\n`;
                    dayTotalQuestions += q.correct + q.wrong;
                    dayTotalCorrect += q.correct;
                    dayTotalWrong += q.wrong;
                }
            }
            if (dayTotalQuestions === 0) {
                report += "  - Soru çözülmedi.\n";
            } else {
                report += `  Toplam Soru: ${dayTotalQuestions}\n`;
            }

            report += `  Okunan Sayfa: ${dayData.pages_read}\n`;
            report += `  Yazılan Not: ${dayData.notes_written}\n`;

            const dayStudyHours = Math.floor(dayData.study_time / 3600);
            const dayStudyMinutes = Math.floor((dayData.study_time % 3600) / 60);
            report += `  Çalışma Süresi: ${dayStudyHours}s ${dayStudyMinutes}d\n\n`;

            weeklyTotalQuestions += dayTotalQuestions;
            weeklyTotalCorrect += dayTotalCorrect;
            weeklyTotalWrong += dayTotalWrong;
            weeklyTotalPages += dayData.pages_read;
            weeklyTotalNotes += dayData.notes_written;
            weeklyTotalStudyTime += dayData.study_time;
        }
    }

    report += "--- Haftalık Toplamlar ---\n";
    report += `Toplam Çözülen Soru: ${weeklyTotalQuestions}\n`;
    report += `Toplam Doğru: ${weeklyTotalCorrect}\n`;
    report += `Toplam Yanlış: ${weeklyTotalWrong}\n`;
    let weeklyAccuracy = 0;
    if (weeklyTotalQuestions > 0) {
        weeklyAccuracy = ((weeklyTotalCorrect / weeklyTotalQuestions) * 100).toFixed(1);
    }
    report += `Haftalık Doğruluk: ${weeklyAccuracy}%\n`;
    report += `Toplam Okunan Sayfa: ${weeklyTotalPages}\n`;
    report += `Toplam Yazılan Not: ${weeklyTotalNotes}\n`;
    const weeklyStudyHours = Math.floor(weeklyTotalStudyTime / 3600);
    const weeklyStudyMinutes = Math.floor((weeklyTotalStudyTime % 3600) / 60);
    report += `Toplam Çalışma Süresi: ${weeklyStudyHours}s ${weeklyStudyMinutes}d\n`;

    alert(report);
}

// Bugünü sıfırla
function resetToday() {
    hapticFeedback();
    if (confirm('Bugünün verilerini sıfırlamak istediğinizden emin misiniz? Bu işlem geri alınamaz!')) {
        const todayKey = getTodayKey();
        if (studyData[todayKey]) {
            delete studyData[todayKey];
            saveData();
            // Reset current timer values
            stopTimer(); // Ensure timer is stopped and data is saved before reset
            elapsedTime = 0;
            startTime = null;
            document.getElementById('timer').textContent = '00:00:00';
        }
        updateDisplay();
        alert('Bugünün verileri sıfırlandı!');
    }
}

// Uygulama yüklendiğinde
window.addEventListener('DOMContentLoaded', () => {
    updateClock();
    setInterval(updateClock, 1000); // Her saniye saati güncelle

    loadData(); // Verileri yükle
    updateDisplay(); // Ekranı ilk kez güncelle

    // İlk yüklemede timer durumunu kontrol et
    const todayData = getTodayData();
    if (todayData.study_time > 0) {
        elapsedTime = todayData.study_time * 1000; // Saniyeyi milisaniyeye çevir
        document.getElementById('timer').textContent = `${Math.floor(elapsedTime / 3600000).toString().padStart(2, '0')}:${Math.floor((elapsedTime % 3600000) / 60000).toString().padStart(2, '0')}:${Math.floor((elapsedTime % 60000) / 1000).toString().padStart(2, '0')}`;
    }
});