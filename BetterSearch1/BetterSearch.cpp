/*
#include <iostream>
#include "sqlite3.h"

int main() {
    sqlite3* db;
    int result = sqlite3_open(":memory:", &db); // Open a temporary in-memory database

    if (result == SQLITE_OK) {
        std::cout << "SQLite is working!" << std::endl;
    }
    else {
        std::cerr << "SQLite failed to initialize!" << std::endl;
    }

    sqlite3_close(db);
    return 0;
}
*/