import streamlit as st
import numpy as np
import os
from typing import List, Callable


def clean_tokens(tokens: List[str]) -> List[str]:
    tokens = [t.replace(" ", "") for t in tokens]
    return tokens

def tokens_for_folder(folder: str, filter: Callable[[str], bool] = lambda x: True) -> List[str]:
    tokens: List[str] = []
    for file in os.listdir(folder):
        if filter(file):
            with open(folder + "/" + file) as f:
                tokens.extend(f.read().split())
    tokens = clean_tokens(tokens)
    return tokens

def tokens_for_file(file):
    tokens: List[str] = []
    with open(file) as f:
        tokens = f.read().split()
    tokens = clean_tokens(tokens)
    return tokens

def tokens_for_string(str: str) -> List[str]:
    return clean_tokens(str.split())

def calculate_transition_matrix(tokens: List[str]) -> np.ndarray:
    
    unique_tokens = list(set(tokens))
    unique_word_combination_counts = {}
    total_froms = {}

    transition_matrix = np.zeros((len(unique_tokens), len(unique_tokens)))

    for i, token in enumerate(tokens):
        if i < len(tokens) - 1:
            from_to = (token, tokens[i + 1])
            unique_word_combination_counts[from_to] = unique_word_combination_counts.get(from_to, 0) + 1
            total_froms[token] = total_froms.get(token, 0) + 1

    for key, value in unique_word_combination_counts.items():
        _from, _to = key 
        
        transition_matrix[unique_tokens.index(_from), unique_tokens.index(_to)] = value / total_froms[_from]
        
    return transition_matrix

def generate_text(tokens: List[str], length: int, P_matrix: np.ndarray, P_init: np.ndarray=None) -> str:
    unique_tokens = list(set(tokens))
    
    text = []
    if P_init is not None:
      current_token = np.random.choice(unique_tokens, p=P_init) 
    else:
        current_token = np.random.choice(unique_tokens)
    
    text.append(current_token)
    for i in range(length):
        # Token should not be the last token in the text as there is no probability of transitioning from it to anything
        while current_token == tokens[-1]:
            current_token = np.random.choice(unique_tokens)
    
        current_token = np.random.choice(unique_tokens, p=P_matrix[unique_tokens.index(current_token)])
        text.append(current_token)
    return " ".join(text)


example_text_mapping = {
    "Las Vegas (German)": "text.txt",
    "Sport (German)": "text2.txt"
}

st.write("# Generate Text")
st.write("This is a simple text generator that uses a Markov chain to generate text.")

source_text = st.text_area("Paste a soruce text here:")
initial_word = st.text_input("Start with this word (has to be in the source text):")
length = st.number_input("Length of the generated text:", value=100)
show_transition_matrix = st.checkbox("Show transition matrix")


st.sidebar.write("### Example Texts")
selected_example_text = st.sidebar.selectbox("Select Example Text", ["Custom", "Las Vegas (German)", "Sport (German)"])


if st.button("Generate Text"):
    with st.spinner("Generating text"):

        if selected_example_text != "Custom":
                    tokens = tokens_for_file(example_text_mapping[selected_example_text])
        else:
            tokens = tokens_for_string(source_text)

        unique_tokens = list(set(tokens))

        if len(tokens) == 0:
            st.error("No text found in the source text area")
        elif len(tokens) == 1:
            st.write("### Generated text:")
            st.write(tokens[0])
            if show_transition_matrix:
                st.write("### Transition matrix:")
                st.write(np.zeros((1, 1)))
        else:            
            P_matrix = calculate_transition_matrix(tokens)

            P_init = None
            if initial_word in unique_tokens:
                P_init = np.zeros(len(unique_tokens))
                P_init[unique_tokens.index(initial_word)] = 1

            text = generate_text(tokens, length, P_matrix, P_init)

            st.write("### Generated text:")
            st.write(text)

            st.write("Length of source text:", len(tokens))

            if show_transition_matrix:
                st.write("### Transition matrix:")
                st.write("Shape:", P_matrix.shape)
                st.write(P_matrix)


