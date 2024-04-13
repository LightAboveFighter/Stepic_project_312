# Slippery moments
### gift_processing
- Single/multiple choice
    - Sample size hardcoded to 10: if you have a question with 11 or more possible answers, then sample_size will be limited to 10
    - If you have questions with partially correct answers, any answer that receives more than 0% of the total possible score will be considered a correct answer.
        > Example:
        >
        > ```gift
        > ::Q1:: What two people are entombed in Grant's tomb? {
        >    ~%-100%No one
        >    ~%0%Every one         #incorrect
        >    ~%1%Grant             #correct
        >    ~%99%Grant's wife     #correct
        >    ~%-100%Grant's father
        > }
        > ```

### pygiftparserrgmf lib
- matching
    - if you have 2 or fewer items to match, the question will be treated as Short().
        > Example:
        >
        > ```gift
        > Which animal eats which food? { 
        >    =cat -> cat food
        >    =dog -> dog food
        > }
        > ```