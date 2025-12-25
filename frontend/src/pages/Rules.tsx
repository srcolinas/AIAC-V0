import './Rules.css'

export default function Rules() {
  return (
    <div className="rules-page">
      <div className="rules-container animate-slide-up">
        <header className="rules-header">
          <h1>The Laws of Teyuna</h1>
          <p className="rules-subtitle">
            A guide to building your legacy in the shadow of the sacred Sierra Nevada
          </p>
        </header>
        
        {/* Introduction */}
        <section className="rules-section">
          <h2>🏔️ Introduction</h2>
          <div className="rules-content">
            <p>
              <strong>Teyuna</strong> is a strategy board game for 3-4 players, inspired by the ancient 
              Tayrona civilization that flourished in the Sierra Nevada de Santa Marta region of 
              present-day Colombia. The Tayrona built the magnificent city of Teyuna (known today as 
              Ciudad Perdida, or "The Lost City"), featuring over 160 terraces carved into the mountainside.
            </p>
            <p>
              In this game, you take on the role of a leader seeking to build the most prosperous 
              settlement in the mountains. Gather resources, construct buildings, and trade with 
              neighbors to achieve glory and honor the ways of your ancestors.
            </p>
          </div>
        </section>
        
        {/* Objective */}
        <section className="rules-section">
          <h2>🎯 Objective</h2>
          <div className="rules-content">
            <p>
              Be the first player to reach <strong>10 Victory Points</strong>. Victory points are 
              earned by:
            </p>
            <ul className="vp-list">
              <li><span className="vp">1 VP</span> for each <strong>Bohío</strong> (settlement)</li>
              <li><span className="vp">2 VP</span> for each <strong>Templo</strong> (temple/city)</li>
              <li><span className="vp">2 VP</span> for <strong>Longest Path</strong> (5+ connected roads)</li>
              <li><span className="vp">2 VP</span> for <strong>Largest Army</strong> (3+ warrior cards played)</li>
              <li><span className="vp">1 VP</span> for certain <strong>Wisdom Cards</strong></li>
            </ul>
          </div>
        </section>
        
        {/* Resources */}
        <section className="rules-section">
          <h2>💎 Resources</h2>
          <div className="rules-content">
            <p>Five sacred resources power your settlement:</p>
            
            <div className="resource-grid">
              <div className="resource-card">
                <span className="resource-icon">🥇</span>
                <h4>Oro (Gold)</h4>
                <p>Extracted from the <strong>Sierra</strong> mountains. Essential for building temples.</p>
              </div>
              
              <div className="resource-card">
                <span className="resource-icon">🪨</span>
                <h4>Piedra (Stone)</h4>
                <p>Quarried from the <strong>Canteras</strong>. Used for terraces, paths, and foundations.</p>
              </div>
              
              <div className="resource-card">
                <span className="resource-icon">☁️</span>
                <h4>Algodón (Cotton)</h4>
                <p>Harvested from <strong>Tierras Altas</strong> (highlands). For textiles and trade.</p>
              </div>
              
              <div className="resource-card">
                <span className="resource-icon">🌽</span>
                <h4>Maíz (Maize)</h4>
                <p>Cultivated in the fertile <strong>Valles</strong>. Sustains your growing community.</p>
              </div>
              
              <div className="resource-card">
                <span className="resource-icon">🌳</span>
                <h4>Madera (Wood)</h4>
                <p>Gathered from the <strong>Selva</strong> (jungle). For construction and tools.</p>
              </div>
            </div>
          </div>
        </section>
        
        {/* Buildings */}
        <section className="rules-section">
          <h2>🏛️ Buildings</h2>
          <div className="rules-content">
            <div className="building-list">
              <div className="building-item">
                <div className="building-header">
                  <span className="building-icon">🛤️</span>
                  <h4>Camino de Piedra (Stone Path)</h4>
                </div>
                <div className="building-cost">
                  Cost: <span>🪨 1 Stone</span> + <span>🌳 1 Wood</span>
                </div>
                <p>
                  Stone paths connect your settlements and allow expansion. Build paths on the 
                  edges between hexes. You can only build a bohío at the end of an unbroken chain 
                  of your own paths.
                </p>
              </div>
              
              <div className="building-item">
                <div className="building-header">
                  <span className="building-icon">🏠</span>
                  <h4>Bohío (Traditional House)</h4>
                </div>
                <div className="building-cost">
                  Cost: <span>🪨 1 Stone</span> + <span>🌳 1 Wood</span> + <span>☁️ 1 Cotton</span> + <span>🌽 1 Maize</span>
                </div>
                <p>
                  The circular bohío is the traditional dwelling of the Tayrona. Build on intersections 
                  (vertices) to collect resources from adjacent hexes. Each bohío is worth 
                  <strong> 1 Victory Point</strong>.
                </p>
              </div>
              
              <div className="building-item">
                <div className="building-header">
                  <span className="building-icon">🏛️</span>
                  <h4>Templo (Temple)</h4>
                </div>
                <div className="building-cost">
                  Cost: <span>🥇 3 Gold</span> + <span>🌽 2 Maize</span>
                </div>
                <p>
                  Upgrade an existing bohío into a sacred temple. Temples collect 2 resources 
                  instead of 1 from adjacent hexes. Each temple is worth <strong>2 Victory Points</strong>.
                </p>
              </div>
            </div>
          </div>
        </section>
        
        {/* Turn Structure */}
        <section className="rules-section">
          <h2>🎲 Turn Structure</h2>
          <div className="rules-content">
            <p>On your turn, follow these phases in order:</p>
            
            <div className="phase-list">
              <div className="phase">
                <div className="phase-number">1</div>
                <div className="phase-content">
                  <h4>Roll the Dice</h4>
                  <p>
                    Roll two dice. The sum determines which hexes produce resources. All players 
                    with bohíos or temples adjacent to hexes with matching numbers receive resources.
                  </p>
                </div>
              </div>
              
              <div className="phase">
                <div className="phase-number">2</div>
                <div className="phase-content">
                  <h4>The Conquistador (Rolling a 7)</h4>
                  <p>
                    If you roll a 7, no resources are produced. Instead:
                  </p>
                  <ul>
                    <li>Any player with more than 7 cards must discard half (rounded down)</li>
                    <li>Move the Conquistador to any hex</li>
                    <li>Steal 1 random resource from a player with a building adjacent to that hex</li>
                  </ul>
                  <p>
                    <em>The Conquistador represents the threat of Spanish invasion. While on a hex, 
                    that hex produces no resources.</em>
                  </p>
                </div>
              </div>
              
              <div className="phase">
                <div className="phase-number">3</div>
                <div className="phase-content">
                  <h4>Trade & Build</h4>
                  <p>
                    You may perform any of these actions in any order, as many times as you can afford:
                  </p>
                  <ul>
                    <li><strong>Trade</strong> with other players or at ports</li>
                    <li><strong>Build</strong> paths, bohíos, or temples</li>
                    <li><strong>Buy</strong> Wisdom Cards</li>
                    <li><strong>Play</strong> Wisdom Cards</li>
                  </ul>
                </div>
              </div>
              
              <div className="phase">
                <div className="phase-number">4</div>
                <div className="phase-content">
                  <h4>End Turn</h4>
                  <p>Pass the dice to the next player.</p>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        {/* Wisdom Cards */}
        <section className="rules-section">
          <h2>📜 Cartas de Sabiduría (Wisdom Cards)</h2>
          <div className="rules-content">
            <p>
              Purchase wisdom cards for <strong>🥇 1 Gold + ☁️ 1 Cotton + 🌽 1 Maize</strong>. 
              These represent the ancestral knowledge of the Tayrona.
            </p>
            
            <div className="card-list">
              <div className="wisdom-card">
                <h4>⚔️ Guerrero Naoma (Naoma Warrior)</h4>
                <p>
                  Move the Conquistador and steal a resource. Playing 3 warriors earns you 
                  "Largest Army" (2 VP).
                </p>
              </div>
              
              <div className="wisdom-card">
                <h4>🌾 Abundancia de la Tierra (Earth's Abundance)</h4>
                <p>
                  Immediately take any 2 resources of your choice from the supply.
                </p>
              </div>
              
              <div className="wisdom-card">
                <h4>🔮 Sabiduría del Mama (Mama's Wisdom)</h4>
                <p>
                  Name a resource. All other players must give you all cards of that type.
                  <em> (Mamas are the spiritual leaders of the Tayrona)</em>
                </p>
              </div>
              
              <div className="wisdom-card">
                <h4>🛤️ Nuevos Caminos (New Paths)</h4>
                <p>
                  Immediately build 2 stone paths for free.
                </p>
              </div>
              
              <div className="wisdom-card">
                <h4>🏆 Avance Ancestral (Ancestral Advancement)</h4>
                <p>
                  Worth 1 Victory Point. Keep this card secret until you win!
                </p>
              </div>
            </div>
          </div>
        </section>
        
        {/* Trading */}
        <section className="rules-section">
          <h2>🤝 Trading</h2>
          <div className="rules-content">
            <p>Trade resources to get what you need:</p>
            
            <ul>
              <li>
                <strong>Player Trade:</strong> On your turn, propose trades to other players. 
                Both parties must agree. Only the active player may initiate trades.
              </li>
              <li>
                <strong>Port Trade:</strong> If you have a bohío on a port:
                <ul>
                  <li>General ports: Trade 3 of any one resource for 1 of any other</li>
                  <li>Specialized ports: Trade 2 of the specific resource for 1 of any other</li>
                </ul>
              </li>
              <li>
                <strong>Bank Trade:</strong> Without a port, trade 4 of any one resource for 1 of any other.
              </li>
            </ul>
          </div>
        </section>
        
        {/* Special Rules */}
        <section className="rules-section">
          <h2>⚖️ Special Rules</h2>
          <div className="rules-content">
            <div className="special-rule">
              <h4>Longest Path</h4>
              <p>
                The player with the longest continuous chain of connected paths (minimum 5) 
                holds "Longest Path" and receives 2 VP. If another player builds a longer 
                chain, they take this achievement.
              </p>
            </div>
            
            <div className="special-rule">
              <h4>Largest Army</h4>
              <p>
                The player who has played the most Naoma Warrior cards (minimum 3) holds 
                "Largest Army" and receives 2 VP. If another player plays more warriors, 
                they take this achievement.
              </p>
            </div>
            
            <div className="special-rule">
              <h4>The Centro Ceremonial</h4>
              <p>
                One hex represents the sacred ceremonial center. It produces no resources 
                and is where the Conquistador begins the game.
              </p>
            </div>
          </div>
        </section>
        
        {/* History */}
        <section className="rules-section cultural-note">
          <h2>📖 About the Tayrona</h2>
          <div className="rules-content">
            <p>
              The Tayrona were a Pre-Columbian civilization that inhabited the Sierra Nevada 
              de Santa Marta in Colombia from approximately 200 CE to 1600 CE. They were 
              master builders, creating an extensive network of stone-paved paths, terraces, 
              and settlements throughout the mountain range.
            </p>
            <p>
              Their most famous achievement is <strong>Teyuna</strong>, also known as 
              <strong> Ciudad Perdida</strong> (The Lost City), built around 800 CE—some 
              650 years before Machu Picchu. The city features over 160 terraces carved into 
              the mountainside, connected by a network of tiled roads and stone staircases.
            </p>
            <p>
              The Tayrona were also renowned for their goldwork, which can be seen today in 
              the Museo del Oro in Bogotá. Their descendants—the Kogi, Arhuaco, Wiwa, and 
              Kankuamo peoples—still live in the Sierra Nevada and consider it the "Heart 
              of the World."
            </p>
            <p className="cultural-respect">
              <em>
                This game is created with deep respect for the Tayrona civilization and their 
                descendants. We encourage players to learn more about this remarkable culture 
                and support indigenous communities in Colombia.
              </em>
            </p>
          </div>
        </section>
      </div>
    </div>
  )
}

