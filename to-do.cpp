#include <iostream>
#include <string>
using namespace std;

int main() {
  int salary;
  double taxes;

  cout << "Enter your salary: " << endl;
  cin >> salary;

  cout << "Enter your taxes: " << endl;
  cin >> taxes;

  double profit = salary * taxes;

  cout << "Your final profit is: " << profit << endl;

  if (profit >= 1000) {
    cout << "High salary earner" << endl;
  }
  else if (profit >= 500) {
    cout << "Medium salary earner" << endl;
  }
  else {
    cout << "Low salary eaner" <<endl;
  }

  return 0;
}
