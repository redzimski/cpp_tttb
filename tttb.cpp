#include "csv.hpp" 
#include <iostream>
using namespace csv;

/* Defining a struct that can represent each row
of CPDB_for_TTTB.csv (the .csv file containing all
Bible verses:) */

struct Verse_Row {
    int verse_id;
    std::string ot_nt;
    std::string book;
    int book_num;
    std::string chapter_num; // This is actually a string, since
    // some values are 'P' (for 'prologue').
    int verse_num;
    std::string verse_code;
    std::string verse;
    int characters;
    int typed;
    double best_wpm;
};

int main() {


// Creating a vector that can store all of the Bible verses:

std::vector<Verse_Row> vrv; // vrv is short for 'Verse Row vector.'

/* Reading data:
This code was based largely on 
https://github.com/vincentlaucsb/csv-parser?tab=
readme-ov-file#indexing-by-column-names
and on
page 22 of A Tour of C++, 2nd Edition by Bjarne Stroustrup. */
std::string verses_file_path = "../Files/CPDB_for_TTTB.csv";
CSVReader reader(verses_file_path);
for (auto& row: reader) {
    Verse_Row vr;
    vr.verse_id = row["Verse_ID"].get<int>();
    vr.ot_nt = row["OT_NT"].get<std::string>();
    vr.book = row["Book"].get<std::string>();
    vr.book_num = row["Book_Num"].get<int>();
    vr.chapter_num = row["Chapter_Num"].get<std::string>();
    vr.verse_num = row["Verse_Num"].get<int>();
    vr.verse_code = row["Verse_Code"].get<std::string>();
    vr.verse = row["Verse"].get<std::string>();
    vr.characters = row["Characters"].get<int>();
    vr.typed = row["Typed"].get<int>();
    vr.best_wpm = row["Best_WPM"].get<double>();
    vrv.push_back(vr);
}

std::cout << "Imported Bible .csv file successfully.\n";
std::cout << "Number of verses imported: " << vrv.size() << "\n";

// Creating a list of unread verses (in the form of vrv indices):
// (Maybe pointers to verses could be used here instead?)

std::vector<int> untyped_verse_indices;

for (int i=0; i <vrv.size(); ++i) {
    if (vrv[i].typed == 0) {
    untyped_verse_indices.push_back(i);}
    };

std::cout << untyped_verse_indices.size() << " verses have not yet \
been typed.\n"; 

if (untyped_verse_indices.size() > 0) {
std::cout << "Here is the next verse that hasn't been typed:\n";
std::cout << vrv[untyped_verse_indices[0]].verse << "\n";
}

/* Saving the updated copy of our table of verses to a .csv file for 
testing purposes: */

/* This section was based on the documentation found at
https://github.com/vincentlaucsb/csv-parser?
tab=readme-ov-file#writing-csv-files
and 
https://vincela.com/csv/classcsv_1_1DelimWriter.html .*/


std::ofstream verse_output_filename {verses_file_path};
auto verses_writer = make_csv_writer(verse_output_filename);

    // Writing header row to .csv file:
    // It's crucial that the order of these rows matches the order
    // of the corresponding field entries within cols_as_strings.
    std::vector<std::string> header_row = {
    "Verse_ID",
    "OT_NT",
    "Book",
    "Book_Num",
    "Chapter_Num",
    "Verse_Num",
    "Verse_Code",
    "Verse",
    "Characters",
    "Typed",
    "Best_WPM"};

    // Writing this header to the .csv file:
    verses_writer << header_row;
    
    // Converting the fields within each row into a vector
    // of strings:
    // See 
    // https://stackoverflow.com/a/23855901/13097194
    // (which actualy recommends a potentially better solution
    // outside of the stanard library) for to_string().
    for (int i=0; i < vrv.size(); ++i) {
    std::vector<std::string> cols_as_strings = {
    std::to_string(vrv[i].verse_id),
    vrv[i].ot_nt,
    vrv[i].book,
    std::to_string(vrv[i].book_num),
    vrv[i].chapter_num,
    std::to_string(vrv[i].verse_num),
    vrv[i].verse_code,
    vrv[i].verse,
    std::to_string(vrv[i].characters),
    std::to_string(vrv[i].typed),
    std::to_string(vrv[i].best_wpm)
    };
    verses_writer << cols_as_strings;
    };





std::cout << "Finished running program.";

}