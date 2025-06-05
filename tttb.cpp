/* Some of this code was based on the hello_world.cc example
at https://github.com/hosseinmoein/DataFrame/blob/master/
examples/hello_world.cc . */

#include <DataFrame/DataFrame.h>
#include <iostream>

using namespace hmdf;
using LDataFrame = StdDataFrame<long>;
/* This DataFrame type isn't present in the Hello World file,
but I decided to make the index column the same 'long' type
as most of the other columns. Hence, I needed to initialize
the DataFrame type using <long> rather than <ulong> (which would
have raised the following error:
terminate called after throwing an instance of 'std::bad_any_cast') */



int main() {

LDataFrame df_Bible;
df_Bible.read("../Files/CPDB_for_TTTB.csv", io_format::csv2);
std::cout << "Imported Bible .csv file successfully.\n";
 
std::cout << df_Bible.get_index().size() << "Verses have been imported.";

/* Saving a copy of this DataFrame to a .csv file for 
testing purposes: */

df_Bible.write<long, double, std::string, 
std::size_t>("../Files/CPDB_for_TTTB_from_program.csv", 
io_format::csv2);


// Creating a filtered copy of df_Bible that shows only
// untyped verses: (that way, the user can start at the first 
// verse that hasn't yet been typed.)

// Creating a selector object that can then be passed to
// get_data_by_sel:
// The 'long &' type refers to the index; the 'long &val' refers
// to the column (in this case, 'Typed') by which we want to filter
// the DataFrame.
auto untyped_selector = [](const long &, const long &val)-> bool {
    return (val == 0);
    };
/* Calling get_data_by_sel():
The first 'long' type refers to the type of the 'Typed' 
value by which to filter the DataFrame; the subsequent 3 types
(double, long, and std::string) encompass all types of the
DataFrame. Based on the documentation (see links below), I think
I need to enter long both before and after the decltype() argument.
(See https://github.com/hosseinmoein/DataFrame/blob/master/
examples/hello_world.cc) and 
https://htmlpreview.github.io/?https://github.com/hosseinmoein/
DataFrame/blob/master/docs/HTML/get_data_by_sel.html
for more details on this function. */
auto df_Bible_untyped = df_Bible.get_data_by_sel<long, 
decltype(untyped_selector), double, long, std::string>(
"Typed", untyped_selector);

std::cout << df_Bible_untyped.get_index().size() << "Verses still \
need to be typed.";

std::cout << "Finished running script";

// Writing df_Bible_untyped to a .csv file for debugging purposes:
df_Bible_untyped.write<long, double, std::string, 
std::size_t>("../Files/untyped_verses.csv", 
io_format::csv2);

}