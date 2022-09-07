import itertools
import logging


def test_func(image, **kwargs):
    for key, value in kwargs.items():
        print(f"{key} : {value}")
    print("End")


class Filter:
    def __init__(self, function, name: str = "UNDEFINED", **kwargs):
        self.parameters = dict()
        for k, v in kwargs.items(): # all parameters must be wrapped in a list
            if isinstance(v, list):
                self.parameters[k] = v
            else:
                self.parameters[k] = [v]

        self.function = function
        self.name = name

        # pack into list to prevent exhaustion of iterator
        self.all_parameter_combinations = list(itertools.product(*self.parameters.values()))
        self.parameter_names = list(self.parameters.keys())

    def __call__(self, image) -> dict:
        generated_images = dict()

        # Apply filtering function to all parameter combinations
        # Store them in the dict with a name that contains the parameter values
        for parameter_combination in self.all_parameter_combinations:
            parameter_dict = dict(zip(self.parameter_names, parameter_combination))
            new_name = f"{self.name}_" + "_".join([f"{name}={value}" for name, value in parameter_dict.items()])
            # try:
            generated_images[new_name] = self.function(image, **parameter_dict)
            # except Exception as e:
            #     logging.error(f"Error ({self.name} with parameters {parameter_dict}): {e}")
            #     return dict()

        return generated_images

    def get_filter_strings(self):
        names = list()
        for parameter_combination in self.all_parameter_combinations:
            parameter_dict = dict(zip(self.parameter_names, parameter_combination))
            names.append(f"{self.name}_" + "_".join([f"{name}={value}" for name, value in parameter_dict.items()]))

        return names
