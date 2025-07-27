/*

#include <iostream>
#include <filesystem>
#include <unordered_map>
#include <vector>
#include <string>
#include <thread>
#include <mutex>

namespace fs = std::filesystem;

std::unordered_map<std::string, std::vector<std::string>> fileIndex;
std::mutex indexMutex;

// Function to index files and directories
void indexFiles(const fs::path& directory) {
    try {
        for (const auto& entry : fs::recursive_directory_iterator(directory, fs::directory_options::skip_permission_denied)) {
            try {
                std::string name = entry.path().filename().string();
                std::string fullPath = entry.path().string();

                // Lock mutex before modifying the index
                std::lock_guard<std::mutex> lock(indexMutex);
                fileIndex[name].push_back(fullPath);
            }
            catch (const std::exception& e) {
                // Ignore permission errors but continue indexing
                std::cerr << "Skipping: " << e.what() << '\n';
            }
        }
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
    }
}

// Function to search indexed files and folders
void searchFiles(const std::string& keyword) {
    std::lock_guard<std::mutex> lock(indexMutex);

    std::vector<std::string> results;
    for (const auto& [name, paths] : fileIndex) {
        if (name.find(keyword) != std::string::npos) {
            results.insert(results.end(), paths.begin(), paths.end());
        }
    }

    if (results.empty()) {
        std::cout << "No files found matching \"" << keyword << "\"\n";
    }
    else {
        std::cout << "\nSearch Results:\n";
        for (size_t i = 0; i < results.size(); ++i) {
            std::cout << i + 1 << ". " << results[i] << '\n';
        }
    }
}

int main() {
    std::string directory = "C:/";  // Change to another drive if needed

    std::cout << "Indexing files... Please wait.\n";
    std::thread indexThread(indexFiles, directory);
    indexThread.join();  // Wait for indexing to finish

    std::cout << "Indexing complete! You can now search for files.\n";

    while (true) {
        std::string keyword;
        std::cout << "\nEnter search keyword (or type 'exit' to quit): ";
        std::getline(std::cin, keyword);

        if (keyword == "exit") break;

        searchFiles(keyword);
    }

    return 0;
}

*/