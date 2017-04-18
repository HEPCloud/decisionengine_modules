#include <iostream>
#include <fstream>

#include "ErrorHandler/ma_rule_engine.h"
#include "ErrorHandler/json/json.h"

void alarm_fn(std::string const & a, std::string const & b)
{
}

void cond_match(std::string const & a)
{
}

int main(int argc, char ** argv)
{
    fhicl::ParameterSet conf;

    if (argc > 1)
    {
        std::ifstream in(argv[1], std::ifstream::binary);

        if (in.is_open())
        {
            in >> conf;
            in.close();
        }
    }

    Json::StyledWriter writer;
    std::cout << writer.write(conf);

    novadaq::errorhandler::ma_rule_engine engine(conf, &alarm_fn, &cond_match);

    std::map<std::string, bool> facts;
    facts.insert(std::make_pair("c1", false));
    facts.insert(std::make_pair("c2", true));

    engine.execute(facts);
    engine.execute(facts);
    
    std::cout << "hello world\n";
    return 0;
}
