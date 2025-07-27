#include <QApplication>
#include <QMainWindow>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QWidget>
#include <QLineEdit>
#include <QComboBox>
#include <QLabel>
#include <QTableWidget>
#include <QTableWidgetItem>
#include <QHeaderView>
#include <QMenuBar>
#include <QStatusBar>
#include <QColor>
#include <unordered_map>

class BetterSearchApp : public QMainWindow {
    Q_OBJECT

public:
    BetterSearchApp(QWidget* parent = nullptr) : QMainWindow(parent) {
        setWindowTitle("BetterSearch");
        setGeometry(100, 100, 900, 500);
        setStyleSheet("background-color: #2E2E2E; color: white;");

        // Main Widget
        QWidget* centralWidget = new QWidget(this);
        QVBoxLayout* mainLayout = new QVBoxLayout(centralWidget);

        // Menu Bar
        QMenuBar* menuBar = this->menuBar();
        menuBar->setStyleSheet(R"(
            QMenuBar { background-color: #1F1F1F; color: white; font-size: 14px; padding: 5px; }
            QMenuBar::item:selected { background-color: #444; }
        )");

        QStringList menuNames = { "File", "Edit", "View", "Search", "Settings", "Help" };
        for (const QString& name : menuNames) {
            menuBar->addMenu(name);
        }

        // Search Bar Layout
        QHBoxLayout* searchLayout = new QHBoxLayout();
        QLineEdit* searchEntry = new QLineEdit();
        searchEntry->setPlaceholderText("Search...");
        searchEntry->setStyleSheet(R"(
            background-color: white; color: black; padding: 8px;
            border-radius: 5px; border: 1px solid #bbb;
        )");

        QComboBox* filterDropdown = new QComboBox();
        filterDropdown->addItems({ "All", "Documents", "Audio", "Images", "Compressed", "Executables" });
        filterDropdown->setStyleSheet(R"(
            background-color: white; color: black; padding: 6px;
            border-radius: 5px; border: 1px solid #bbb;
        )");

        searchLayout->addWidget(searchEntry);
        searchLayout->addWidget(filterDropdown);
        mainLayout->addLayout(searchLayout);

        // Table Widget
        table = new QTableWidget();
        table->setColumnCount(4);
        table->setHorizontalHeaderLabels({ "Name", "Path", "Size", "Date Modified" });
        table->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);

        table->setStyleSheet(R"(
            QTableWidget { background-color: #3A3A3A; border: 1px solid #555; color: white; gridline-color: black; font-size: 14px; }
            QHeaderView::section { background-color: #1F1F1F; padding: 5px; border: none; font-size: 14px; color: white; }
            QTableWidget QTableCornerButton::section { background-color: #1F1F1F; }
        )");

        mainLayout->addWidget(table);

        // Status Bar
        QLabel* statusLabel = new QLabel("1,000,000 results");
        statusLabel->setStyleSheet("padding: 5px; color: white; font-size: 14px;");
        statusBar()->addWidget(statusLabel);

        // Populate Table
        populateTable();

        setCentralWidget(centralWidget);
    }

private:
    QTableWidget* table;

    void populateTable() {
        struct FileData {
            QString name, path, size, date;
        };

        std::vector<FileData> files = {
            // Documents
            {"Project_Report.docx", "C:/Users/User/Documents/Reports", "850 KB", "2024-03-05 14:30"},
            {"Resume.docx", "C:/Users/User/Documents/Work", "120 KB", "2024-03-06 09:45"},
            {"Meeting_Notes.docx", "C:/Users/User/Documents/Meetings", "500 KB", "2024-03-04 11:10"},

            // Audio
            {"Podcast_Episode1.wav", "C:/Music/Podcasts", "4.8 MB", "2024-02-28 10:15"},
            {"Guitar_Solo.mp3", "C:/Music/Recordings", "6.2 MB", "2024-03-01 08:30"},
            {"Nature_Sounds.wav", "C:/Music/Samples", "5.1 MB", "2024-03-02 18:45"},

            // Images
            {"Beach_Sunset.png", "C:/Pictures/Vacation", "3.2 MB", "2024-02-28 16:20"},
            {"Family_Photo.jpg", "C:/Pictures/Family", "4.5 MB", "2024-03-01 12:40"},
            {"Mountain_View.png", "C:/Pictures/Landscapes", "2.9 MB", "2024-03-03 09:15"},

            // Compressed
            {"Backup_Files.zip", "C:/Backups", "200 MB", "2024-03-06 12:10"},
            {"Project_Archive.rar", "C:/Archives/Projects", "80 MB", "2024-02-25 17:55"},
            {"Photos_Collection.7z", "C:/Archives/Photos", "150 MB", "2024-02-27 19:30"},

            // Executables
            {"Setup_Wizard.exe", "C:/Program Files/Setup", "45 MB", "2024-02-20 08:05"},
            {"Game_Launcher.exe", "C:/Games/Launcher", "55 MB", "2024-02-18 14:00"},
            {"Software_Updater.exe", "C:/Program Files/Updater", "22 MB", "2024-03-01 13:50"}
        };

        std::unordered_map<QString, QString> colorMap = {
            {"docx", "#66A3FF"}, {"mp3", "#FFAA66"}, {"wav", "#FFAA66"},
            {"jpg", "#66A3FF"}, {"png", "#66A3FF"}, {"zip", "#FF6666"},
            {"rar", "#FF6666"}, {"7z", "#FF6666"}, {"exe", "#FFFFFF"}
        };

        table->setRowCount(files.size());

        for (size_t row = 0; row < files.size(); ++row) {
            const auto& [name, path, size, date] = files[row];
            QString extension = name.section('.', -1);  // Extract file extension
            QColor bgColor(colorMap.count(extension) ? colorMap[extension] : "#444");

            QList<QTableWidgetItem*> items = {
                new QTableWidgetItem(name),
                new QTableWidgetItem(path),
                new QTableWidgetItem(size),
                new QTableWidgetItem(date)
            };

            for (auto* item : items) {
                item->setBackground(bgColor);
                item->setForeground(bgColor.lightness() > 150 ? Qt::black : Qt::white);
            }

            for (int col = 0; col < 4; ++col) {
                table->setItem(row, col, items[col]);
            }
        }
    }
};

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    BetterSearchApp window;
    window.show();
    return app.exec();
}
