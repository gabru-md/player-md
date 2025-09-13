# radio-md

### A project for creating calming, generative music with rhythmic patterns.

`radio-md` is a unique project that blends music and technology to create calming, generative music. By using your favorite rhythmic patterns and instrumental choices, like the ukulele, it can create a personalized and soothing audio experience.

-----

## Features

  * **Generative Music:** Creates unique musical pieces based on user-defined inputs.
  * **Rhythmic Patterns:** Uses your preferred rhythmic patterns as a foundation for the music.
  * **Instrumental Focus:** Specifically designed to work with instruments like the ukulele.

-----

## How to use it

The project is built on Python and can be run from the command line.

### Prerequisites

  * Python 3.9
  * The required libraries listed in `requirements.txt`.

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/gabru-md/radio-md
    ```
2.  Navigate into the project directory:
    ```bash
    cd radio-md
    ```
3.  Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Script

Use the `radio.py` script to generate music. You can customize the output using various command-line arguments.

Here is an example command:

```bash
python3 radio.py --keys C,G,D,F,Bb,Am,Em,Dm --narratives 2 --repeat 2 --ui --bpm 72
```

  * `--keys`: A comma-separated list of musical keys.
  * `--narratives`: The number of narratives to use in the music.
  * `--repeat`: The number of times to repeat a section.
  * `--ui`: Enables the user interface.
  * `--bpm`: The beats per minute.

-----

## Contributing

Contributions are welcome\! If you have ideas for new features, bug fixes, or improvements, please open an issue or submit a pull request.

-----