#include <boost/python.hpp>
#include <string>
#include <vector>
#include <map>
#include <iostream>

using namespace std;
using namespace boost::python;

struct RuleEngine
{
    RuleEngine(string const & rules, string const & facts)
    {
        cout << "rules = " << rules << "\n";
        cout << "facts = " << facts << "\n";
    }

    boost::python::tuple execute( boost::python::dict const & facts)
    {
        auto fnames = facts.keys();
        for(int i=0; i<len(fnames); ++i)
        {
            cout << (string)extract<string>(fnames[i]) << " : " 
                 << extract<bool>(facts[fnames[i]]) << "\n";
        }

        list actions;
        list new_facts;

        actions.append("action");
        new_facts.append("fact");

        return boost::python::make_tuple(actions, new_facts);
    }
};


BOOST_PYTHON_MODULE(RE)
{
    class_<RuleEngine>("RuleEngine", init<string, string>())
        .def("execute", &RuleEngine::execute)
    ;
};

