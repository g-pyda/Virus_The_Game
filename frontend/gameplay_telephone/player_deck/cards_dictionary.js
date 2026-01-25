const cards = {
    medicines: {
        blue: "/gameplay_telephone/player_deck/cards/medicines/medicine_blue.png",
        green: "/gameplay_telephone/player_deck/cards/medicines/medicine_green.png",
        rainbow: "/gameplay_telephone/player_deck/cards/medicines/medicine_rainbow.png",
        red: "/gameplay_telephone/player_deck/cards/medicines/medicine_red.png",
        yellow: "/gameplay_telephone/player_deck/cards/medicines/medicine_yellow.png"
    },
    organs: {
        yellow: "/gameplay_telephone/player_deck/cards/organs/o_bone.png",
        blue: "/gameplay_telephone/player_deck/cards/organs/o_brain.png",
        red: "/gameplay_telephone/player_deck/cards/organs/o_heart.png",
        green: "/gameplay_telephone/player_deck/cards/organs/o_stomach.png",
        rainbow: "/gameplay_telephone/player_deck/cards/organs/o_uterus.png"
    },
    special: {
        doctors_mistake: "/gameplay_telephone/player_deck/cards/special/s_doctors_mistake.png",
        latex_glove: "/gameplay_telephone/player_deck/cards/special/s_latex_glove.png",
        organ_thief: "/gameplay_telephone/player_deck/cards/special/s_organ_thief.png",
        pandemics: "/gameplay_telephone/player_deck/cards/special/s_pandemics.png",
        transplant: "/gameplay_telephone/player_deck/cards/special/s_transplant.png"
    },
    virus: {
        blue: "/gameplay_telephone/player_deck/cards/virus/virus_blue.png",
        green: "/gameplay_telephone/player_deck/cards/virus/virus_green.png",
        rainbow: "/gameplay_telephone/player_deck/cards/virus/virus_rainbow.png",
        red: "/gameplay_telephone/player_deck/cards/virus/virus_red.png",
        yellow: "/gameplay_telephone/player_deck/cards/virus/virus_yellow.png"
    },
    back: "/gameplay_telephone/player_deck/cards/card.png"
};

export function getCard(category, type) {
    return cards[category][type];
}

export function getEmpty(){
    return cards['back']
}

export function setCardImage(cardId, category, type) {
    const cardElement = document.getElementById(cardId);
    if (cardElement) {
        cardElement.src = getCard(category, type);
    }
}

export function disableAllPlayButtons() {
    const playButtons = document.querySelectorAll('button .play-btn');
    playButtons.forEach(button => {
        button.disabled = true;
    });
}

export function disableAllDiscardButtons() {
    const discardButtons = document.querySelectorAll('button .discard-btn');
    discardButtons.forEach(button => {
        button.disabled = true;
    });
}

export function enableContinueButton() {
    const continueButtons = document.querySelectorAll('button .continue-btn');
    continueButtons.forEach(button => {
        button.disabled = false;
    });
}