export const MessageCategories = {
    GENERAL_PRAISE: 'generalPraise',
    LOW_MISTAKES: 'lowMistakes',
    FAST_COMPLETION: 'fastCompletion',
    MOTIVATION_FOR_IMPROVEMENT: 'motivationForImprovement',
    FRIENDLY_ENCOURAGEMENT: 'friendlyEncouragement',
    REALLY_WELL: 'reallyWell',
    CREATIVE_AND_FUN: 'creativeAndFun'
};

export const messages = {
    [MessageCategories.GENERAL_PRAISE]: [
        `Fantastic work! You completed the level in just {time} seconds with only {mistakes} mistakes. Keep it up!`,
        `Great job! It took you {time} seconds to finish, and you’re improving every step of the way!`,
        `Well done! With only {mistakes} mistakes and a time of {time} seconds, you’re mastering these letters quickly!`,
        `Awesome effort! Just {time} seconds to finish this level. Let’s aim for even fewer mistakes next time!`,
        `You did it! {time} seconds and {mistakes} mistakes—your hard work is paying off!`
    ],
    [MessageCategories.LOW_MISTAKES]: [
        `Wow! Only {mistakes} mistakes this level! Your focus is fantastic!`,
        `Amazing! {mistakes} mistakes in {time} seconds? That’s incredible progress!`,
        `So close to perfection! {time} seconds and just {mistakes} mistakes. You’re on fire!`
    ],
    [MessageCategories.FAST_COMPLETION]: [
        `Speedy and sharp! You finished the level in just {time} seconds. Can you go even faster next time?`,
        `Lightning quick! {time} seconds flat. Keep pushing, and you’ll be unstoppable!`
    ],
    [MessageCategories.MOTIVATION_FOR_IMPROVEMENT]: [
        `Good effort! You completed the level in {time} seconds. Let’s focus on cutting down those {mistakes} mistakes!`,
        `Well done! {mistakes} mistakes this time. Try for even fewer in the next level!`,
        `Every mistake is a learning opportunity! You finished in {time} seconds, and you’ll get even better.`,
        `Keep going! {time} seconds and {mistakes} mistakes mean you’re making solid progress.`
    ],
    [MessageCategories.FRIENDLY_ENCOURAGEMENT]: [
        `Great job! Remember, practice makes perfect. On to the next level!`,
        `Fantastic effort! No matter the time or mistakes, you’re doing great!`,
        `Keep up the amazing work! Your brain is getting stronger every level!`,
        `Another level mastered! You’re building skills step by step. Awesome!`
    ],
    [MessageCategories.REALLY_WELL]: [
        `Perfect score! No mistakes and {time} seconds—this level didn’t stand a chance against you!`,
        `Wow, you’re a pro! You conquered this level with {time} seconds and no mistakes!`
    ],
    [MessageCategories.CREATIVE_AND_FUN]: [
        `You’re climbing to the top like a spelling wizard! {time} seconds and {mistakes} mistakes this time.`,
        `That level didn’t know what hit it! {time} seconds and {mistakes} mistakes—great stuff!`,
        `Alphabet champ! You’re making those letters look easy in {time} seconds.`,
        `You aced that level faster than a cheetah! {time} seconds and just {mistakes} mistakes!`,
        `Your brainpower is unstoppable! {time} seconds and only {mistakes} mistakes. Let’s keep the momentum!`
    ]
};