/* Typing test code that makes use of the cpp-terminal library
(https://github.com/jupyter-xeus/cpp-terminal)
This code is based in part on that project's documentation.
*/

#include "cpp-terminal/terminal.hpp"
#include "cpp-terminal/color.hpp"
#include <iostream>
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
#include <chrono>

std::string verse = "And God said, \"Let there be light.\" \
And light became.";
int verse_length = verse.length();


int main()
{// }
/* Some of the following code was based on the documentation at
https://github.com/jupyter-xeus/cpp-terminal/blob/master/examples/keys.cpp .*/

std::cout << "Your next verse to type is:\n" << verse << "\nThis \
verse is " << verse_length << " characters long.\n";
std::cout << "Press any key to begin the typing test." << "\n";

Term::terminal.setOptions(Term::Option::NoClearScreen, 
Term::Option::NoSignalKeys, Term::Option::Cursor, 
Term::Option::Raw);
if(!Term::is_stdin_a_tty()) { throw Term::Exception(
    "The terminal is not attached to a TTY and therefore \
can't catch user input. Exiting..."); }
// The following code was based in part on 
// https://github.com/jupyter-xeus/cpp-terminal/blob/master/examples/events.cpp .
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
bool exit_program = false;
while ((user_string != verse) & (exit_program == false)){
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
{exit_program = true;
}
else if (keyname == "Backspace") // We'll need to remove the 
// last character from our string.
{user_string = user_string.substr(0, user_string.size() -1);
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
    for (int j = user_string.size() -1; j >= 0; --j)
    {
        if ((isspace(user_string[j])) && 
        (j != (user_string.size() -1)))
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
if (user_string == verse.substr(0, user_string.size()))
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

double wpm = (verse_length / test_seconds) * 12; /* To calculate WPM,
we begin with characters per second, then multiply by 60 (to go
from seconds to minutes) and divide by 5 (to go from characters
to words using the latter's standard definition).*/

std::cout << "You typed the " << verse_length << "-character verse \
in " << test_seconds << " seconds, which reflects a typing speed \
of " << wpm << " WPM.";
}
