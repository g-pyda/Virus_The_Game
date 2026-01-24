const cards = {
    medicines: {
        blue: "cards/medicines/medicine_blue.png",
        green: "cards/medicines/medicine_green.png",
        rainbow: "cards/medicines/medicine_rainbow.png",
        red: "cards/medicines/medicine_red.png",
        yellow: "cards/medicines/medicine_yellow.png"
    },
    organs: {
        bone: "cards/organs/o_bone.png",
        brain: "cards/organs/o_brain.png",
        heart: "cards/organs/o_heart.png",
        stomach: "cards/organs/o_stomach.png",
        uterus: "cards/organs/o_uterus.png"
    },
    special: {
        doctors_mistake: "cards/special/s_doctors_mistake.png",
        latex_glove: "cards/special/s_latex_glove.png",
        organ_thief: "cards/special/s_organ_thief.png",
        pandemics: "cards/special/s_pandemics.png",
        transplant: "cards/special/s_transplant.png"
    },
    virus: {
        blue: "cards/virus/Virus_blue.png",
        green: "cards/virus/virus_green.png",
        rainbow: "cards/virus/virus_rainbow.png",
        red: "cards/virus/virus_red.png",
        yellow: "cards/virus/virus_yellow.png"
    },
    back: "cards/card.png"
};

function getCard(category, type) {
    return cards[category][type];
}

function getEmpty(){
    return cards[back]
}

function setCardImage(cardId, category, type) {
    const cardElement = document.getElementById(cardId);
    if (cardElement) {
        cardElement.src = getCard(category, type);
    }
}

function disableAllPlayButtons() {
    const playButtons = document.querySelectorAll('.card-row .btn:first-child');
    playButtons.forEach(button => {
        button.disabled = true;
    });
}