# CURATIVE CALCULATOR
#
# This class is a curative calculator, it uses the formula for curative calculation
# found by John DeMar in his propellant notes linked below
# https://www.thrustgear.com/topics/Curative_calculation.pdf
# 
# This class takes in liquid ingredients other than curatives (binder, plasticizer etc.)
# and returns the required amount of curative for that mix

import sys

## Brief - performs the curative calculation
def main():

  agents = collectInput()

  e_curative = agents[0]
  cure_ratio = agents[1]

  summation = 0
  for ingredient in agents[2:]:
    (percent, equivalent) = ingredient
    summation += percent/equivalent

  percent_curative = e_curative * cure_ratio * summation
  formatCurative = format(percent_curative, '.2f')
  print('The recommend percent curative for this liquid composition is: ' + str(formatCurative))
  print('\n\nThank you for using the SARP curative calculator!')

## Brief - collects user input and returns required composition of the curative
# returns the various agents for curative composition calculation
def collectInput():

  agents = []

  print('Welcome to SARPs curative calculator!\n')
  agents.append(float(input('Enter curative equivalent weight (###): ')))
  agents.append(float(input('Enter cure ratio (#.#): ')))
  print('\n')

  counter = 1
  while True:

    print('Enter liquid ingredient #' + str(counter) + ' Information')
    percent_ingredient = float(input('Percent of mix (##.##): '))
    equivalent_weight = float(input('Equivalent weight of ingredient (###): '))

    while percent_ingredient <= 0 or equivalent_weight <= 0:
      print('invalid input re enter information')
      percent_ingredient = input('Percent of mix (##.##): ')
      equivalent_weight = input('Equivalent weight of ingredient (###): ')

    ingredient = (percent_ingredient, equivalent_weight)
    agents.append(ingredient)
  
    again = input('Would you like to enter another ingredient (y/n): ')
    if again != 'yes' and again != 'y':
      break

    print('\n')

    counter += 1

  return agents

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()
