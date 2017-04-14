#include <iostream>

#include "ErrorHandler/ma_rule_engine.h"

void alarm_fn(std::string const & a, std::string const & b)
{
}

void cond_match(std::string const & a)
{
}

int main()
{
    fhicl::ParameterSet conf;
    novadaq::errorhandler::ma_rule_engine engine(conf, &alarm_fn, &cond_match);

    msg_t msg;
    engine.feed(msg);
    
    std::cout << "hello world\n";
    return 0;
}
