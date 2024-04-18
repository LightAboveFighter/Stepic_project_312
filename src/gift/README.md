# Slippery moments
### gift_processing
- Single/multiple choice
    - Sample size hardcoded to 10: if you have a question with 11 or more possible answers, then sample_size will be limited to 10
    - If you have questions with partially correct answers, any answer that receives more than 0% of the total possible score will be considered a correct answer.
        [**Example**](https://github.com/LightAboveFighter/Stepic_project_312/blob/394a410d20732b539a3325f3307c7838b67a0609/tests/gift_examples/Slippery_moments.gift#L2-L8)<br>
        

### pygiftparserrgmf lib
- matching
    - if you have 2 or fewer items to match, the question will be treated as Short().
        [**Example**](https://github.com/LightAboveFighter/Stepic_project_312/blob/394a410d20732b539a3325f3307c7838b67a0609/tests/gift_examples/Slippery_moments.gift#L10-L13)<br>
