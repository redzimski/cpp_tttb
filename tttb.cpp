/* C++ Version of Type Through the Bible
(Still a very early work in progress!)

By Kenneth Burchfiel
Released under the MIT License

Link to project's GitHub page:
https://github.com/kburchfiel/cpp_tttb

This code also makes extensive use of the following 
open-source libraries:

1. Vincent La's CSV parser (https://github.com/vincentlaucsb/csv-parser)
2. CPP-Terminal (https://github.com/jupyter-xeus/cpp-terminal)

In addition, this program uses the Catholic Public Domain Version
of the Bible that Ronald L. Conte put together. This Bible can be 
found at https://sacredbible.org/catholic/ I last updated my local
copy of this Bible (whose text does get updated periodically)
around June 10, 2025.

Blessed Carlo Acutis, pray for us!

To dos (very incomplete list)!
    1. Allow a new test to start immediately after the last one 
    (e.g. 'marathon mode')

    2. Implement an autosave option in which files get saved
    after every 5 tests or so. (This will get trickier if you
    implement parts 4 and 5, since you won't have a full copy
    of word and test results to refer to.)

    3. Think about ways to show and analyze stats (ideally using
    C++, but perhaps via Python also)

    4. Consider skipping the process of loading your existing
    word_results data into memory. You won't really need it for
    anything within the program, and by the time you type through 
    the whole Bible, this file could be around 33 MB in size.

    5. Similarly, consider skipping the process of loading test
    result data into memory.

    6. Prevent the program from crashing if the user doesn't enter
    an integer when specifying a verse number.

    7. Add code that accounts for a case in which all verses
    have been typed.

    8. Add in code that accounts for cases in which the most recent
    verse that you typed was the last verse in the Bible.

    9. In a separate script, compare the speed of (1) loading items
    into a vector of values, then passing them by value; (2) loading
    items into a vector of values, then passing them by reference 
    (your current approach); (3) loading items into a vector of 
    unique pointers to values, then passing them by reference or
    by value; and (4) creating a unique pointer to a vector, then
    loading items into it. (You could have a simulated dataset of
    1 million rows with 1,000 columns each, then add each row's
    columns together.)

*/



#include <iostream>
#include <ctime>
#include <chrono>
#include <map>
#include <memory>
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

std::string all_verses_typed_message = "All verses have already \
been typed at least once! try another choice (such as i for a \
non-marathon-mode session or s for a marathon-mode session).\n";

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
// (Since this data will be used to populate all rows within
// the test results CSV file, it will need to include all
// of the rows within that file as well. However, not all of 
// the attributes stored here will actually end up within
// that file.)
struct Test_Result_Row {
    long unix_test_end_time;
    std::string local_test_end_time;
    int verse_id;
    std::string verse;
    double wpm;
    double test_seconds;
    bool completed_test;
    double error_rate;
    double error_and_backspace_rate;
    // This struct will be expanded to include accuracy data,
    // the time the test was started and finished, and possibly other
    // items also. 
};

// Defining a struct that can store word-level WPM information:
// (This struct will be used to keep track of WPM results for 
// individual words within tests.)

struct Word_Result_Row 
{
std::string word = "";
// Initializing certain variables as -1 or -1.0 will make it 
// easier to identify cases in which they weren't updated.
// I could try this approach with other structs as well.
long last_character_index = -1; 
// The starting character could also be stored, but since this
// value will be used as a map key, it will probably be redundant to
// include it here also. 
long word_length = -1; // an int would likely work fine here.
double wpm = -1.0;
double test_seconds = -1.0;
double error_rate = -1.0;
double error_and_backspace_rate = -1.0;
};

int select_verse_id(std::vector<Verse_Row>& vrv) {
/* This function allows the player to select a certain ID. It also
checks for errors in order to (hopefully!) prevent the game
from crashing. 
Note: I had originally set the value typed by the user to an 
integer, then checked to see whether cin was valid; however,
this created a strange (to me) bug in which the function would
work fine the first time, but not during subsequent uses.
I did include cin.clear() and cin.ignore() calls, but to no avail.
Therefore, I decided to read in a string, then use a try/except
block to handle it. This approach is working much better,
thankfully!*/
std::string id_response_as_str = "";
while (true) {
std::cout << "Enter the ID of the verse that you would like \
to type. This ID can be found in the first column of \
the CPDB_for_TTTB.csv file. To exit out of this option, type -1.\n";
// Checking for a valid response:
std::cin >> id_response_as_str;
try
{int id_response_as_int = std::stoi(id_response_as_str);

if (id_response_as_int == -1)
{std::cout << "Never mind, then!\n";
return -1;}

else if ((id_response_as_int >= 1) && (
    id_response_as_int <= vrv.size()))
// Subtracting 1 from id_response_as_int will get us the index 
// position of that verse (as the index of each verse is one less 
// than its ID).
{return (id_response_as_int -1);
}
else
{std::cout << "That is not a valid ID. Please try again.\n";
//return -1;
}
}

catch (...) {
    std::cout << "Your input was invalid. Please try again.\n";
//return -1;
}
}
}


std::map<long, Word_Result_Row> gen_word_result_map(
    const std::string& verse) 
/*This function will go through each character within the verse
passed to it in order to identify all words within the verse;
their starting and ending characters; and their lengths. This 
information will then be stored within a map of Word_Result_Row objects
that the typing test code can access in order to calculate word-level
WPM data.*/
{
// Initializing several variables here so that they can get 
// utilized within the following loops:
int first_character_index = -1;
std::string newword = "";
std::map<long, Word_Result_Row> word_map;


// Checking for the first character within the verse that starts
// a word:
for (int i = 0; i < verse.size(); i++)
{if (isalnum(verse[i] != 0))
first_character_index = i;
newword = verse[i];
break;
}

// std::cout << "Current values of first_character_index \
// and newword: " << first_character_index << " " << newword << "\n";

// Now that we know where the first character that starts a word 
// is located,
// we can continue to retrieve the other characters (starting
// from the character following this first character).


for (int i = first_character_index +1; i < verse.size(); i++)

    {
    /*If a character is alphanumeric, and the one prior to it
    was not, we'll consider this to be the start of a new word.
     Note that isalnum returns either a 0 or non-0 number
     (see https://en.cppreference.com/w/cpp/string/byte/isalnum; 
     in my case, it was 8), which is why I'm checking for 
     0 and non-0 in my if statement. This code could likely 
     be simplified, however.*/
        if ((isalnum(verse[i]) != 0) & (
            isalnum(verse[i-1]) == 0))
        {first_character_index = i;
        newword = verse[i]; // I had previously tried to 
        // create a Word_Result_Row class here and assign verse[i] to 
        // its .word attribute, but this failed to work correctly.
        // std::cout << "Starting character info: " 
        // << i << " " << verse[i] << "\n";
        }

        
        else if (((isalnum(verse[i]) == 0) 
        && (isalnum(verse[i-1]) != 0)) || (
        (isalnum(verse[i]) != 0) 
        && (i == (verse.size() -1))))
        /*In this case, either verse[i-1] marks the end of a word, 
        or the final character of the verse is part of a word. 
        For both of these situations, we should go ahead and add 
        this word to a new Word_Result_Row object, then add that object
        to our word map (with the initial character as the key). */
        {int last_character_index = i-1;
        // Changing this value to i if the second condition 
        // (e.g. the final word within the verse is a letter) is true:

        if ((isalnum(verse[i]) != 0) 
        && (i == (verse.size() -1)))
         {
            last_character_index = i;
            // In this case, we'll need to add this final character
            // to newword also.
            newword+= verse[i];}
        // Creating a new Word_Result_Row object that can store
        // various attributes about this word:
        Word_Result_Row wr;
        wr.word = newword;
        wr.word_length = newword.size();
        wr.last_character_index = last_character_index;
        word_map[first_character_index] = wr;
        // std::cout << "Ending character info: " << i << " " 
        // << verse[i-1] << "\n";
        }

        else if (isalnum(verse[i]) != 0)
        // In this case, we're in the middle of constructing a word,
        // so we'll go ahead and add this alphanumeric character
        // to that word.
        {newword += verse[i];}

    }
            

    // Printing out all initial characters, ending characters, 
    // and words within the map for debugging purposes:

    // for (auto const& [starting_character, word_result] : word_map) 
    // {std::cout << word_result.word << ": characters " << 
    // starting_character << " to " << 
    // word_result.last_character_index
    // << " (" << word_result.word_length << " characters long)\n";}

    // Moving word_map in order to avoid an unnecessary copy:
    return std::move(word_map);
};



bool run_test(
    Verse_Row& verse_row, std::vector<Test_Result_Row>& trrv, 
std::vector<Word_Result_Row>& wrrv, bool marathon_mode) 
    {
/* Some of the following code was based on the documentation at
https://github.com/jupyter-xeus/cpp-terminal/blob/
master/examples/keys.cpp .*/

// Calling gen_word_result_map() to create a map that contains 
// information about each word within the verse:
// (This will prove useful when calculating word-level WPM data.)

std::map<long, Word_Result_Row> word_map = gen_word_result_map(
    verse_row.verse);

// Initializing several variables that will be used later in
// this function:
// Initializing counters that will keep track of the number of
// errors the user made:
// (One of these counters won't count backspaces as errors;
// the other will.)
long error_counter = 0;
long backspace_counter = 0;
long word_error_counter = 0;
long word_backspace_counter = 0;

//Initializing a string to which characters typed by the user
// will be added: (This will allow us to print the entire portion
// of the verse that the user has typed so far, rather than just
// the most recent character.)
std::string user_string = "";
bool exit_test = false;
bool completed_test = true;
int last_character_index = -1;
// For debugging:
std::string last_character_index_as_string = "";
//std::string word_timing_note = ""; // for debugging
int latest_first_character_index = -1;
int first_character_index = -1;
long word_length = 0;
auto word_start_time = std::chrono::high_resolution_clock::now();


// Initializing our terminal:
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


if (marathon_mode == false) // The following prompt should be skipped
// within marathon mode, thus allowing users to go directly 
// into the typing test.
{
Term::cout << "Your next verse to type is:\n" << 
verse_row.verse << "\nThis \
verse is " << verse_row.characters << " characters long.\nPress \
any key to begin the typing test." << std::endl;

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
start_test = true;
break;
}
default: break;
    }
};
}

//Clearing the screen before the start of the test:
// cursor_move(1,1) moves the cursor to the top left of the terminal.
// Note that, for this to work, we need to pass
// this function call to Term::cout (it doesn't do 
// anything by itself). Note that passing it to std::cout won't work.
// The kilo.cpp example (available at
// https://github.com/jupyter-xeus/cpp-terminal/blob/master/examples/kilo.cpp
// and the cursor.cpp source code at 
// https://github.com/jupyter-xeus/cpp-terminal/blob/master/cpp-terminal/cursor.cpp
// helped me recognize all this.)
// I've also found that ending Term::cout lines with "\n" may 
// not work; instead, it may be necessary to use std::endl .

Term::cout << Term::cursor_move(1,1) << 
Term::clear_screen() << verse_row.verse << std::endl;


// Starting our timing clock: 
// (This code was based on p. 1010 of The C++ Programming Language,
// 4th edition.)
auto start_time = std::chrono::high_resolution_clock::now();

/* Checking to see whether the first character begins 
one of the words in word_map: (This will generally, but not 
always be the case.)
If so, we'll need to begin word-timing-related 
processes immediately.
*/

if (word_map.contains(0))
{
// Updating latest_first_character_index:
latest_first_character_index = 0;
    last_character_index = word_map[
    0].last_character_index;
word_start_time = start_time;

word_length = word_map[0].word_length;
last_character_index_as_string = std::to_string(
    last_character_index);
// word_error_counter and word_backspace_counter
// were already initialized to 0 earlier within 
// this function, so we don't
// need to re-initialize them as 0 here.
// word_timing_note = "the first letter within the verse \
// began a word. its corresponing ending character index \
// is: "+last_character_index_as_string;
}

// Users may wish to exit a given test before completing it,
// so we should accommodate that choice.
// However, in that case, this boolean will be set to 'false' so that
// we don't mistake the exited test for a completed one.
while ((user_string != verse_row.verse) & (exit_test == false)){
Term::Event event = Term::read_event();
switch(event.type())
{case Term::Event::Type::Key:
{
Term::Key key(event);
// Creating a timer following this keypress:
// (This will be useful for timing how long it took the user
// to type each individual word.)
auto keypress_time = std::chrono::high_resolution_clock::now();

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
backspace_counter++; // Since the user pressed backspace,
// we'll need to increment this counter by 1 so that this
// keypress can get reflected within our error_and_backspace_counter
// value.
word_backspace_counter++;
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
{backspace_counter++; 
word_backspace_counter++;
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
if (user_string == verse_row.verse.substr(0, user_string.length()))
// Checking to see whether we should start or end our word timer:
{// Checking to see whether we should begin timing a new word:
// This new word's index position will be one greater than 
// the current index position--but, conveniently, user_string.length()
// allows us to access that position. And we'll want to 
// start the timing right before the first letter of the word so that
// the time that it takes that letter to get typed can also get
// included in the overall timing for the word.
// The code also checks to see whether the length of the user's entry
// is greater than the most recent first_character_index so that
// the user can't 'get out of' or restart the current word timer by 
// going back to the start of the current word or a previous word.
    if ((word_map.contains(user_string.length()))
    && (long(user_string.length()) > latest_first_character_index))
    // Note that string.length() needs to be cast to a long or int
    // in order to get compared with latest_first_character_index.

{// Updating latest_first_character_index:
latest_first_character_index = user_string.length();
    last_character_index = word_map[
    latest_first_character_index].last_character_index;
word_start_time = keypress_time;
// Resetting word-specific error and backspace counters:
word_error_counter = 0;
word_backspace_counter = 0;

word_length = word_map[
    latest_first_character_index].word_length;
last_character_index_as_string = std::to_string(
    last_character_index);
// word_timing_note = "the next letter will start a word. \
// its corresponing ending character index \
// is: "+last_character_index_as_string;
}
if (user_string.length()-1 == last_character_index)
{// In this case, we've made it to the end of the word whose
// starting character we approached earlier. Thus, we can 
// stop our word timer and create a new Word_Result_Row object
// with our output.
auto word_end_time = keypress_time;
auto word_seconds = std::chrono::duration<double>(
    word_end_time - word_start_time).count();
double word_wpm = (word_length / word_seconds) * 12;
int word_error_and_backspace_counter = \
word_error_counter + word_backspace_counter;
double word_error_rate = (word_error_counter / static_cast<double>(
    word_length));
double word_error_and_backspace_rate = (
    word_error_and_backspace_counter / static_cast<double>(
        word_length));

// word_timing_note = "the end of the word has been \
// reached. Ending character: "+last_character_index_as_string + " \
// word length: "+std::to_string(word_length) + " word \
// duration: "+ std::to_string(word_seconds) + " WPM: " + std::to_string(
// word_wpm);
// Note that, once we arrive at the next word's starting 
// character, certain variables (like last_character_index)
// will get replaced with new versions.

// Storing these details within word_map: (We can use
// latest_first_character_index as a key here.)
word_map[latest_first_character_index].wpm = word_wpm;
word_map[latest_first_character_index].test_seconds = word_seconds;
word_map[latest_first_character_index].error_rate = word_error_rate;
word_map[latest_first_character_index].error_and_backspace_rate = \
word_error_and_backspace_rate;

}



    print_color = Term::Color::Name::Green;}
else // The user made a mistake, as signified by the fact that
// this string doesn't match the initial section of the verse that
// has the same length.
{print_color = Term::Color::Name::Red;
if ((keyname != "Backspace") && (keyname != "Alt+Del")) {
    // In this case, we'll increment our main error
    // counter, as the user did not press Backspace.
    // (This code may need to be updated to also address
    // the use of Ctrl+Backspace, though on my Linux system,
    // that combination also produces the name 'Backspace.')
    error_counter++;
    word_error_counter++;
}
}
/* To print the output, we'll first clear the entire screen and 
move the cursor back to the top left. Next, we'll print both
the original verse and the user's response so far. (This approach 
greatly simplifies our code, as it prevents us from having to
handle challenges like multi-verse output and moving from one 
line to another. It really is simpler to just clear the sceren 
and start anew after each keystroke.

Also note that, in order to debug this output, you'll want to add 
relevant variables (such as word_timing_note) after these items 
rather than earlier in the loop--as Term::clear_screen() will erase
all other post-keypress output.*/

Term::cout << Term::clear_screen() << Term::cursor_move(1,1) 
<< verse_row.verse << std::endl << 
Term::color_fg(print_color) << user_string 
<< color_fg(Term::Color::Name::Default) <<std::endl; 
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
// The following formatting code was based on the examples
    // at
    // https://en.cppreference.com/w/cpp/chrono/c/strftime
    // I could also have used std::format(), but 
    // this isn't available within older C++ implementations.
    // (See https://en.cppreference.com/w/cpp/chrono/
    // system_clock/formatter) for more information on that option.)
    char strftime_container [25];
    std::strftime(strftime_container,
    25, "%FT%T%z", std::localtime(&unix_test_end_time));
    std::string local_time_string = strftime_container;
    // %F represents YYYY-MM-DD; %T represents 
    // HH-MM-SS; and %z represents the local UTC offset
    // (e.g. -0400 for Eastern Daylight Time in the US).
    // (The T in between %F and %T helps differentiate
    // between these two components.)
    // Here's an example of what local_time_string might
    // look like: 
    // 2025-06-12T21:49:33-0400
    // (This string is 24 chararcters long. I found that
    // I needed to set strftime_container as one greater
    // than this length in order for it to fit the entire
    // timestamp.

double wpm = (
    verse_row.characters / test_seconds) * 12; /* To calculate WPM,
we begin with characters per second, then multiply by 60 (to go
from seconds to minutes) and divide by 5 (to go from characters
to words using the latter's standard definition).*/

/* Calculating error rates:
These will be equal to the number of errors divided by 
the number of verses. note that it's possible for 
the rate to be above 100%. Another option would be to
divide the number of erroneous keypresses by the number
of keypresses, but this approach is a bit simpler.
(Calculating these rates as (verse_length - 
error_count)/verse_length) wouldn't be ideal, as we could then
end up with a negative number, which would be confusing.
*/


int error_and_backspace_counter = error_counter + backspace_counter;


// std::cout << "Error counter, backspace counter, error and \
// backspace counter, and verse length: " << error_counter <<
// backspace_counter << error_and_backspace_counter << verse_length;

// Casting verse_length to a double ensures that error_rate itself
// will be a double, not an int (which would likely result in
// an incorrect calculation).
double error_rate = (error_counter / static_cast<double>(
    verse_row.characters));
double error_and_backspace_rate = (
    error_and_backspace_counter / static_cast<double>(
        verse_row.characters));

if (completed_test == true) {
std::cout << "You typed the " << verse_row.characters 
<< "-character verse \
in " << test_seconds << " seconds, which reflects a typing speed \
of " << wpm << " WPM. Your error rate was " << error_rate << " (not \
including backspaces) and " << error_and_backspace_rate << " (\
including backspaces).\n";


/* The code below for looping through a dictionary is based on that
provided by POW at https://stackoverflow.com/a/26282004/13097194 . */

for (auto [word_map_key, word_map_value]: word_map) {
    // std::cout << word_map_value.word << " "
    // << word_map_value.word_length << " " << word_map_value.wpm 
    // << word_map_value.test_seconds << "\n";
    

    /* Adding a new word result row to wrrv: (one row will be added 
    for each word. */
    Word_Result_Row wrr;
    wrr.word = word_map_value.word;
    wrr.wpm = word_map_value.wpm;
    wrr.error_rate = word_map_value.error_rate;
    wrr.error_and_backspace_rate = \
    word_map_value.error_and_backspace_rate;
    wrrv.push_back(wrr);    
    }

    /* Adding a new test result row to trrv: (only one row will
    be added for the entire test.) */
    Test_Result_Row trr;
    trr.unix_test_end_time = unix_test_end_time_as_long;
    trr.local_test_end_time = local_time_string;
    trr.verse_id = verse_row.verse_id;
    trr.verse = verse_row.verse;
    trr.wpm = wpm;
    trr.test_seconds = test_seconds;
    trr.completed_test = completed_test;
    trr.error_rate = error_rate;
    trr.error_and_backspace_rate = error_and_backspace_rate;
    trrv.push_back(trr);

    // Updating the 'typed' value (and, if needed,
    // the 'best_wpm' value) within our verse_row object:
    verse_row.typed = 1;
    if (wpm > verse_row.best_wpm) {
    verse_row.best_wpm = wpm;}

}
else 
{
    std::cout << "Exiting test.\n";
    }

return completed_test;

}


int main() {

//Reading relevant files into our program:


// Creating a vector that can store all of the Bible verses found
// within CPDB_for_TTTB.csv:


// Note: I had considered reading data into a vector of 
// unique pointers to Verse_Row objects; however, based on 
// some online research, I don't think this approach would 
// necessarily speed up my program--and, in fact, all of the
// deferencing operations could end up slowing it down. Therefore,
// I instead decided to have vrv store full copies of this data;
// however, my typing test function accesses values stored in this
// vector by reference, which should reduce the amount of 
// copying involved.
// 

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

// Importing test result data:
// I was also thinking about having trrv store unique pointers
// to test result rows, but I ultimately decided to instead
// have my typing test function access this data by reference,
// as I felt that that would lead to better performance overall.

std::vector<Test_Result_Row> trrv; // trrv is short for 
// 'Test result row vector.'


std::string test_results_file_path = "../Files/test_results.csv";
CSVReader test_results_reader(test_results_file_path);
for (auto& row: test_results_reader) {
    Test_Result_Row trr;
    trr.unix_test_end_time = row["Unix_Test_End_Time"].get<long>();
    trr.local_test_end_time = row["Local_Test_End_Time"].get<>();
    trr.verse_id = row["Verse_ID"].get<int>();
    // The following verse objects could get replaced 
    // with unique pointers also.
    trr.verse = row["Verse"].get<>();
    trr.wpm = row["WPM"].get<double>();
    trr.test_seconds = row["Test_Seconds"].get<double>();
    trr.error_rate = row["Error_Rate"].get<double>();
    trr.error_and_backspace_rate = row[
        "Error_and_Backspace_Rate"].get<double>();
    trr.completed_test = 1; // Essentially a placeholder, though
    // it *is* accurate to say that these tests were completed.
    
    trrv.push_back(trr);
}

std::cout << "Imported test result data (if any) successfully.\n";
std::cout << "Number of test results imported: " 
<< trrv.size() << "\n";


// Importing word result data:

std::vector<Word_Result_Row> wrrv; // wrrv is short for 
// 'Word result row vector.'

std::string word_results_file_path = "../Files/word_results.csv";
CSVReader word_results_reader(word_results_file_path);
for (auto& row: word_results_reader) {
    Word_Result_Row wrr;
    wrr.word = row["Word"].get<>();
    wrr.wpm = row["WPM"].get<double>();
    wrr.error_rate = row["Error_Rate"].get<double>();
    wrr.error_and_backspace_rate = row[
        "Error_and_Backspace_Rate"].get<double>();
    wrrv.push_back(wrr);
}


std::cout << "Imported word result data (if any) successfully.\n";
std::cout << "Number of word results imported: " 
<< wrrv.size() << "\n";


// Counting the number of unread verses so far:

int earliest_untyped_verse_index = 40000; // This number will be 
// updated within the following for loop.

int untyped_verses = 0;
int typed_verses = 0;
bool all_verses_typed = true; // This value will also be used 
// within our main gameplay loop to determine whether or not 
// the user has finished typing all verses at least once.

for (int i=0; i <vrv.size(); ++i) {
    if (vrv[i].typed == 0) {
        if (i < earliest_untyped_verse_index)
        // In this case, our earliest untyped verse index value
        // will be updated to match this smaller value. (We 
        // deliberately initialized that variable to a number
        // higher than our verse count in order to ensure that this
        // update process would work correctly.
    {
        earliest_untyped_verse_index = i;}
    all_verses_typed = false;
    untyped_verses++;}
    else
    {typed_verses++;}
    }


if (untyped_verses != 0)
{std::cout << typed_verses << " verses have been typed so far, \
leaving " << untyped_verses << " untyped. The earliest untyped \
verse has the ID " << earliest_untyped_verse_index+1 << ".\n";}

else {
    std::cout << "All verses have been typed! Congratulations on \
this momentous accomplishment!\n";}

int previously_typed_verse_index = -1; // I chose to initialize
// this integer as -1 so that, when the user selects
// sequential marathon mode at the very start of the program,
// TTTB will select the verse with index 0 (e.g. the first verse
// in the Bible) as their first verse to type.

// Determining whether to run a typing test, and if so, for what 
// verse:
std::string user_response = "";
bool marathon_mode = false;

// Main gameplay loop:
while (user_response != "e")
{

int verse_index_to_type = -1; // We'll check for this value when 
// determining whether to run a typing test. 

// Checking whether either marathon mode is active (and, if so,
// skipping the regular prompt with which users are presented):
if (marathon_mode == false)
{
std::cout << "Enter 'n' to type the next untyped verse; 'c' to type \
the next verse; and 'i' to type a specific verse ID.\n \
To enter 'untyped marathon mode' \
(in which you will continually be presented with the next \
untyped verse until you exit out of a race), press 'm.'\n \
To enter 'sequential marathon mode', in which you will continually \
be asked to type (1) the verse following the one you just typed or \
(2) (when starting this mode) a verse of your choice, enter 's.'\nTo \
exit the program and save your progress, enter 'e'.\n";

std::cin >> user_response;
}
if ((user_response == "n") || user_response == "m")

if (all_verses_typed == true)
{std::cout << all_verses_typed_message; // Since verse_index_to_type 
// is stil at -1, and marathon mode hasn't been set to true, the user
// will now be returned to the main gameplay prompt. 
}
else
{
// Checking for the next verse that hasn't been typed:
// (It's best to perform this check anew whenever the user enters
// this response to account for verses that were specified manually
// via the 'i' argument, then completed.)

// Note: this loop makes use of a previously defined variable 
// that will get updated whenever this loop runs. (That way,
// we won't waste time checking earlier verses that we've already
// checked.)


for (; earliest_untyped_verse_index < vrv.size(); 
++earliest_untyped_verse_index) {
    if (vrv[earliest_untyped_verse_index].typed == 0)
{
    verse_index_to_type = earliest_untyped_verse_index;
    if (user_response == "m")
    {marathon_mode = true;}
break;}
}

if (verse_index_to_type == -1) // In this case, the user has typed
// all verses at least once.
{all_verses_typed = true;
std::cout << all_verses_typed_message;
}

}

else if (user_response == "i")
{verse_index_to_type = select_verse_id(vrv);
}

else if (user_response == "e")
{std::cout << "Exiting typing test.\n";
    // break;
    }

else if ((user_response == "s") || (user_response == "c"))
{
    if (previously_typed_verse_index == (
        vrv.size() - 1)) // In this case, the previously-typed verse 
    // was the last verse in the Bible; therefore, this option
    // won't be valid.
    {std::cout << "You just typed the last verse in the Bible. \
therefore, you'll need to select another option, such as 'i', \
which will allow you to type a specific verse.\n";
marathon_mode = false; // Exiting marathon mode in order to prevent
// an infinite dialog loop from occuring
}
    else
{
    verse_index_to_type = previously_typed_verse_index + 1;
    if (user_response == "s") {
        if (marathon_mode == false) // In this case, the player 
        // has just entered this mode; therefore, we will allow 
        // him/her to select a starting verse.
        {std::cout << "Please select a verse ID from which to start \
this mode.";
        verse_index_to_type = select_verse_id(vrv);
    if (verse_index_to_type != -1) // If the user didn't select
    // a valid verse, we won't want to set marathon mode to true.
    {
    marathon_mode = true;}    
        }
    
    }
}
}

if (verse_index_to_type != -1) // In this case, the user has
// indicated that he/she wishes to type a verse--so we'll go ahead
// and initiate a typing test for the verse in question.
{
    Verse_Row& verse_to_type = vrv[verse_index_to_type];

// Running the typing test: 
// Note: All arguments will be passed as references in order to
// (hopefully) reduce runtime and/or allow certain items,
// namely trrv and wrrv, to get updated directly within the function.
bool completed_test = run_test(
    verse_to_type, trrv, wrrv, marathon_mode);
// The following code will exit a user out of either marathon 
// mode if he/she did not complete the most recent test.
if (completed_test == false) {
    marathon_mode = false;
}

if (completed_test == true)
// Updating previously_typed_verse_index so that it will be 
// ready for use within options 's' and 'c':
{previously_typed_verse_index = verse_index_to_type;}   

}
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

std::cout << "Updated Bible .csv file.\n";

std::ofstream test_results_output_filename {test_results_file_path};
auto test_results_writer = make_csv_writer(
    test_results_output_filename);

    header_row = {
    "Unix_Test_End_Time",
    "Local_Test_End_Time",
    "Verse_ID",
    "Verse",
    "WPM",
    "Test_Seconds",
    "Error_Rate",
    "Error_and_Backspace_Rate"};

    // Writing this header to the .csv file:
    test_results_writer << header_row;
    
    for (int i=0; i < trrv.size(); ++i) {
    std::vector<std::string> cols_as_strings = {
    std::to_string(trrv[i].unix_test_end_time),
    trrv[i].local_test_end_time,
    std::to_string(trrv[i].verse_id),
    trrv[i].verse,
    std::to_string(trrv[i].wpm),
    std::to_string(trrv[i].test_seconds),
    std::to_string(trrv[i].error_rate),
    std::to_string(trrv[i].error_and_backspace_rate),
    };
    test_results_writer << cols_as_strings;
    };

std::cout << "Updated .csv file containing test results.\n";



std::ofstream word_results_output_filename {word_results_file_path};
auto word_results_writer = make_csv_writer(
    word_results_output_filename);

    header_row = {
    "Word",
    "WPM",
    "Error_Rate",
    "Error_and_Backspace_Rate"};

    // Writing this header to the .csv file:
    word_results_writer << header_row;
    
    for (int i=0; i < wrrv.size(); ++i) {
    std::vector<std::string> cols_as_strings = {
    wrrv[i].word,
    std::to_string(wrrv[i].wpm),
    std::to_string(wrrv[i].error_rate),
    std::to_string(wrrv[i].error_and_backspace_rate),
    };
    word_results_writer << cols_as_strings;
    };

std::cout << "Updated .csv file containing word results.\n";


std::cout << "Quitting program.\n";

}