let scrollAmount = 0;

function slideCards(direction) {
  const track = document.getElementById("imageTrack");

  const cardWidth = 268; // image width + gap
  const maxScroll = track.scrollWidth - track.clientWidth;

  scrollAmount += direction * cardWidth;

  // stop below 0
  if (scrollAmount < 0) {
    scrollAmount = 0;
  }

  // stop beyond end
  if (scrollAmount > maxScroll) {
    scrollAmount = maxScroll;
  }

  track.scrollTo({
    left: scrollAmount,
    behavior: "smooth",
  });
}

// auto move forward every 3 sec
setInterval(() => {
  const track = document.getElementById("imageTrack");
  const maxScroll = track.scrollWidth - track.clientWidth;

  if (scrollAmount >= maxScroll) {
    scrollAmount = 0;
  } else {
    scrollAmount += 268;
  }

  track.scrollTo({
    left: scrollAmount,
    behavior: "smooth",
  });
}, 3000);
