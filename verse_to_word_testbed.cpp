# include <iostream>
# include <vector>
# include <map>

// To do: Update the code so that you do two separate passes.
// The first finds all starting characters, and the second
// finds the ending character for those characters. I think
// this will be an easier and more intuitive approach
// than one that tries to do everything within the same loop
// (though that might work also).

std::string verse = "God also said, \"Let there be a \
firmament in the midst of the waters, and let it \
divide waters from waters.\"";

struct Word_Result 
{
std::string word = "";
long last_character_index = 0; 
// The starting character could also be stored, but since this
// value will be used as a map key, it will probably be redundant to
// include it here also. 
long word_length = 0; // an int would likely work fine here.
double wpm = 0;
double test_seconds = 0.0;
long error_count = 0;
long error_and_backspace_count = 0;
double error_rate = 0.0;
double error_and_backspace_rate = 0.0;
};

// The following map will store information related to all words
// within the veres. Its key will be first character of the word
// within the verse.
std::map<long, Word_Result> word_map;

int main() {

// Testing out ways to extract words from the verse:

// You could do a separate loop to find the first character--which 
// would simply be the first alphanumeric character in the verse.
// (You could then start the next loop at that index.)

// Instantiating several variables here so that they can get 
// utilized within the following loops:
int first_character_index = 0;
std::string newword = "";

// Checking for the first character within the verse that starts
// a word:
for (int i = 0; i < verse.size(); i++)
{if (isalnum(verse[i] != 0))
first_character_index = i;
newword = verse[i];
break;
}

std::cout << "Current values of first_character_index \
and newword: " << first_character_index << " " << newword << "\n";

// Now that we know where the first character that starts a word 
// is located,
// we can continue to retrieve the other characters (starting
// from the character following this first character).


for (int i = first_character_index +1; i < verse.size(); i++)

    {//If a character is alphanumeric, and the one prior to it
    // was not, we'll consider this to be the start of a new word.
    // std::cout << "i, verse[i], and verse[i-1]: " << i << 
    // " " << verse[i] << " " << verse[i-1] << " " << isalnum(verse[i])
    //  << " " << isalnum(verse[i-1]) << "\n";
     // Note that isalnum returns either a 0 or non-0 number
     // (see https://en.cppreference.com/w/cpp/string/byte/isalnum; 
     // in my case, it was 8), which is why I'm checking for 
     // 0 and non-0 (rather than true or false) in my if statement.
        if ((isalnum(verse[i]) != 0) & (isalnum(verse[i-1]) == 0))
        {first_character_index = i;
        newword = verse[i]; // I had previously tried to 
        // create a Word_Result class here and assign verse[i] to 
        // its .word attribute, but this failed to work correctly.
        std::cout << "Starting character info: " 
        << i << " " << verse[i] << "\n";}

        
        else if (((isalnum(verse[i]) == 0) 
        && (isalnum(verse[i-1]) != 0)) || ((isalnum(verse[i]) != 0) 
        && (i == (verse.size() -1))))
        // In this case, either verse[i-1] marks the end of a word, 
        // or the final character of a verse is part of a word. 
        // For both of these situations, we should go ahead and add 
        // this word to a new Word_Result object, then add that object
        // to our word map (with the initial character as the key).
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
        // Creating a new Word_Result object that can store
        // various attributes about this word:
        Word_Result wr;
        wr.word = newword;
        wr.word_length = newword.size();
        wr.last_character_index = last_character_index;
        word_map[first_character_index] = wr;
        std::cout << "Ending character info: " << i << " " 
        << verse[i-1] << "\n";}

        else if (isalnum(verse[i]) != 0)
        // In this case, we're in the middle of constructing a word,
        // so we'll go ahead and add this alphanumeric character
        // to that word.
        {newword += verse[i];}

    }
            

    // Printing out all initial characters, ending characters, 
    // and words within the map:

    for (auto const& [starting_character, word_result] : word_map) 
    {std::cout << word_result.word << ": characters " << 
    starting_character << " to " << word_result.last_character_index \
    << " (" << word_result.word_length << " characters long)\n";}


            std::cout << "Finished running script.";
}




