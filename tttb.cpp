/* C++ Version of Type Through the Bible
(Still a very early work in progress!)

By Kenneth Burchfiel
Released under the MIT License

Link to project's GitHub page:
https://github.com/kburchfiel/cpp_tttb

This code also makes use of the following open-source libraries:

1. Vincent La's CSV parser (https://github.com/vincentlaucsb/csv-parser)
2. CPP-Terminal (https://github.com/jupyter-xeus/cpp-terminal)*/

#include <iostream>
#include <ctime>
#include <chrono>
#include "csv.hpp" 
#include "cpp-terminal/terminal.hpp"
#include "cpp-terminal/color.hpp"
#include "cpp-terminal/cursor.hpp"
#include "cpp-terminal/exception.hpp"
#include "cpp-terminal/input.hpp"
#include "cpp-terminal/iostream.hpp"
#include "cpp-terminal/key.hpp"
#include "cpp-terminal/options.hpp"
#include "cpp-terminal/screen.hpp"
#include "cpp-terminal/terminal.hpp"
#include "cpp-terminal/tty.hpp"
#include "cpp-terminal/version.hpp"
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


// Defining a struct that can store relevant test result data:
struct Test_Result_Row {
    long unix_test_end_time;
    std::string local_test_end_time;
    int verse_id;
    std::string verse;
    double wpm;
    double test_seconds;
    bool completed_test;
    // This struct will be expanded to include accuracy data,
    // the time the test was started and finished, and possibly other
    // items also. 
};



Test_Result_Row run_test(int verse_id, 
std::string verse, int verse_length) 
    {
/* Some of the following code was based on the documentation at
https://github.com/jupyter-xeus/cpp-terminal/blob/
master/examples/keys.cpp .*/

std::cout << "Your next verse to type is:\n" << verse << "\nThis \
verse is " << verse_length << " characters long.\n";
std::cout << "Press any key to begin the typing test." << "\n";

Term::terminal.setOptions(Term::Option::NoClearScreen, 
Term::Option::NoSignalKeys, Term::Option::Cursor, 
Term::Option::Raw);
if(!Term::is_stdin_a_tty()) { throw Term::Exception(
    "The terminal is not attached to a TTY and therefore \
can't catch user input. Exiting..."); }
/* The following code was based in part on 
https://github.com/jupyter-xeus/cpp-terminal/blob/
master/examples/events.cpp . */
Term::Cursor cursor{Term::cursor_position()};


// The following while statement allows the user to begin the 
// test immediately after pressing a key. This statement will also
// display the verse following the keypress so that the user can
// reference it when beginning the test. (The verse is displayed at
// the top left so that its location won't change between this 
// section of the script and the following while loop.)
bool start_test = false;
while (start_test == false) {
Term::Event event = Term::read_event();
switch(event.type())
{
    case Term::Event::Type::Key:
{
Term::Key key(event);
// cursor_move(1,1) moves the cursor to the top left of the terminal.
// Note that, for this to work, we need to pass
// this function call to Term::cout (it doesn't do 
// anything by itself). Note that passing it to std::cout won't work.
// The kilo.cpp example (available at
// https://github.com/jupyter-xeus/cpp-terminal/blob/master/examples/kilo.cpp
// and the cursor.cpp source code at 
// https://github.com/jupyter-xeus/cpp-terminal/blob/master/cpp-terminal/cursor.cpp
// helped me recognize all this.)
Term::cout << Term::cursor_move(1,1) << 
Term::clear_screen() << verse << std::endl;
start_test = true;
break;
}
default: break;
    }
};

// Starting our timing clock: 
// (This code was based on p. 1010 of The C++ Programming Language,
// 4th edition.)
auto start_time = std::chrono::high_resolution_clock::now();

//Initializing a string to which characters typed by the user
// will be added: (This will allow us to print the entire portion
// of the verse that the user has typed so far, rather than just
// the most recent character.)
std::string user_string = "";
bool exit_test = false;
bool completed_test = true; // The user may want to exit the 
// test before completing it, so we should accommodate that choice.
// However, in that case, this boolean will be set to 'false' so that
// we don't mistake the exited test for a completed one.
while ((user_string != verse) & (exit_test == false)){
Term::Event event = Term::read_event();
switch(event.type())
{case Term::Event::Type::Key:
{
Term::Key key(event);

std::string char_to_add = ""; // This default setting will 
// be used in certain special keypress cases (including Backspace)
std::string keyname = key.name();

if (keyname == "Space") {
char_to_add = " ";
}
else if (keyname == "Ctrl+C")
{exit_test = true;
completed_test = false;
}
else if (keyname == "Backspace") // We'll need to remove the 
// last character from our string.
{user_string = user_string.substr(0, user_string.length() -1);
}
// For documentation on substr, see
// https://cppscripts.com/string-slicing-cpp
else if (keyname == "Alt+Del") // This behavior is similar to
// Ctrl + Backspace (which seemed to be interpreted as just 
// Backspace by the cpp-terminal library). The following code
// will remove all characters from the end of the string up
// to (but not including) the most recent space. However, 
// if the last character in the string happens to be a space
// as well, the loop will skip over it and search instead
// for the second-to-last space. (That way, repeated Alt+Del
// entries can successfully remove multiple words.)
{
    for (int j = user_string.length() -1; j >= 0; --j)
    {
        if ((isspace(user_string[j])) && 
        (j != (user_string.length() -1)))
    //if (isspace(user_string[j]))
    /* Truncating the response so that it only extends up to 
    the latest space (thus removing all of the characters 
    proceeding that space): */
    {user_string = user_string.substr(0, j+1);
    break;}
    }

}

else {
char_to_add = keyname;
}

user_string += char_to_add;
/* Determining how to color the output: (If the output is correct 
so far, it will be colored green; if there is a mistake, it will
instead be colored red.*/
auto print_color = Term::Color::Name::Default;
if (user_string == verse.substr(0, user_string.length()))
{print_color = Term::Color::Name::Green;}
else
{print_color = Term::Color::Name::Red;}
/* To print the output, we'll first clear the entire screen and 
move the cursor back to the top left. Next, we'll print both
the original verse and the user's response so far. (This approach 
greatly simplifies our code, as it prevents us from having to
handle challenges like multi-verse output and moving from one 
line to another. It really is simpler to just clear the sceren 
and start anew after each keystroke.*/
Term::cout << Term::clear_screen() << Term::cursor_move(1,1) 
<< verse << std::endl << 
Term::color_fg(print_color) << user_string 
<< color_fg(Term::Color::Name::Default) << std::endl;
break;
}
default: break;
}
}

// Ending our timing clock and calculating our WPM:
// (This code was based in part on the examples found at
// https://en.cppreference.com/w/cpp/chrono/duration .)
auto end_time = std::chrono::high_resolution_clock::now();
auto test_seconds = std::chrono::duration<double>(
    end_time - start_time).count();
/* The following time variable initialization code was based in part 
on https://en.cppreference.com/w/cpp/chrono/system_clock/now.html . */
std::time_t unix_test_end_time = std::chrono::
system_clock::to_time_t(end_time);
long unix_test_end_time_as_long = long(unix_test_end_time);
// Creating a string version of this timestamp that shows
// the user's local time:
std::string local_time_string = std::ctime(&unix_test_end_time);

double wpm = (verse_length / test_seconds) * 12; /* To calculate WPM,
we begin with characters per second, then multiply by 60 (to go
from seconds to minutes) and divide by 5 (to go from characters
to words using the latter's standard definition).*/

if (completed_test == true) {
std::cout << "You typed the " << verse_length << "-character verse \
in " << test_seconds << " seconds, which reflects a typing speed \
of " << wpm << " WPM.";}
else 
{
    std::cout << "Exiting test.";
    }


Test_Result_Row trr;
trr.unix_test_end_time = unix_test_end_time_as_long;
trr.local_test_end_time = local_time_string;
trr.verse_id = verse_id;
trr.verse = verse;
trr.wpm = wpm;
trr.test_seconds = test_seconds;
trr.completed_test = completed_test;
// Make sure to add a datetime entry here also (either Unix 
// time or local time--or, ideally, both)

    return trr;
    }


int main() {


// Creating a vector that can store all of the Bible verses found
// within CPDB_for_TTTB.csv:

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

std::vector<Test_Result_Row> trrv; // trrv is short for 
// 'Test result row vector.'


std::string test_results_file_path = "../Files/test_results.csv";
CSVReader test_results_reader(test_results_file_path);
for (auto& row: test_results_reader) {
    Test_Result_Row trr;
    trr.unix_test_end_time = row["Unix_Test_End_Time"].get<long>();
    trr.local_test_end_time = row["Local_Test_End_Time"].get<>();
    trr.verse_id = row["Verse_ID"].get<int>();
    trr.verse = row["Verse"].get<>();
    trr.wpm = row["WPM"].get<double>();
    trr.test_seconds = row["Test_Seconds"].get<double>();
    trr.completed_test = 1; // Essentially a placeholder, though
    // it *is* accurate to say that these tests were completed.
    trrv.push_back(trr);
}


// Creating a list of unread verses (in the form of vrv indices):
// (Maybe pointers to verses could be used here instead?)

std::vector<int> untyped_verse_indices;

for (int i=0; i <vrv.size(); ++i) {
    if (vrv[i].typed == 0) {
    untyped_verse_indices.push_back(i);}
    };

std::cout << untyped_verse_indices.size() << " verses have not yet \
been typed.\n"; 

// if (untyped_verse_indices.size() > 0) {
// std::cout << "Here is the next verse that hasn't been typed:\n";
// std::cout << vrv[untyped_verse_indices[0]].verse << "\n";
// }

std::string user_response = "";
// The following iterator will allow us to move through the list of
// verses that haven't yet been typed.
int untyped_verse_iterator = 0;
while (user_response != "e")
{
std::cout << "To type the next untyped verse, enter 'n'. \
To exit, enter 'e'.";

std::cin >> user_response;

if (user_response == "n")
{
// You may need/want to update the following code so that it stores
// a reference to the row rather than a copy thereof.
Verse_Row next_untyped_verse_row = vrv[
    untyped_verse_indices[untyped_verse_iterator]];
int next_verse_id = next_untyped_verse_row.verse_id;
std::string next_verse = next_untyped_verse_row.verse;
int next_verse_length = next_untyped_verse_row.characters;

Test_Result_Row tres = run_test(next_verse_id, 
next_verse, next_verse_length);

// Adding results of the test to vrv so that it can later get added
// to our .csv file:
/* (To do: Create a standalone file that contains one row per 
test result. */

if (tres.completed_test == true) // We'll only want to make these 
// updates and advance our untyped test iterator
// if the user actually completed the test.
{
vrv[untyped_verse_indices[untyped_verse_iterator]].typed = 1;
if (tres.wpm > vrv[untyped_verse_indices[
    untyped_verse_iterator]].best_wpm) {
vrv[untyped_verse_indices[
    untyped_verse_iterator]].best_wpm = tres.wpm;}
untyped_verse_iterator++; 

// Adding information about this test to our vector of test result
// rows:
trrv.push_back(tres);
}
}


else if (user_response == "e")
{std::cout << "Exiting typing test.\n";
    // break;
    }
// Advancing our untyped verse iterator by 1 so that we can access
// the next untyped verse within our vector of Bible verses:

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



std::ofstream test_results_output_filename {test_results_file_path};
auto test_results_writer = make_csv_writer(
    test_results_output_filename);

    header_row = {
    "Unix_Test_End_Time",
    "Local_Test_End_Time",
    "Verse_ID",
    "Verse",
    "WPM",
    "Test_Seconds"};

    // Writing this header to the .csv file:
    test_results_writer << header_row;
    
    for (int i=0; i < trrv.size(); ++i) {
    std::vector<std::string> cols_as_strings = {
    std::to_string(trrv[i].unix_test_end_time),
    trrv[i].local_test_end_time,
    std::to_string(trrv[i].verse_id),
    trrv[i].verse,
    std::to_string(trrv[i].wpm),
    std::to_string(trrv[i].test_seconds)
    };
    test_results_writer << cols_as_strings;
    };

std::cout << "Quitting program.";

}