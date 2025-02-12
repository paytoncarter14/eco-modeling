using Agents
using Random: Xoshiro
using CairoMakie

@agent struct SchellingAgent(GridAgent{2})
	mood::Bool
	group::Int
end

function schelling_step!(agent, model)
    minhappy = model.min_to_be_happy
    count_neighbors_same_group = 0

    for neighbor in nearby_agents(agent, model)
        if agent.group == neighbor.group
            count_neighbors_same_group += 1
        end
    end

    if count_neighbors_same_group >= minhappy
        agent.mood = true
    else
        agent.mood = false
        move_agent_single!(agent, model)
    end
    return
end

function initialize(; total_agents = 320, gridsize = (20, 20), min_to_be_happy = 5, seed = 125)

    space = GridSpaceSingle(gridsize; periodic = false)
    properties = Dict(:min_to_be_happy => min_to_be_happy)
    rng = Xoshiro(seed)
    model = StandardABM(
        SchellingAgent,
        space;
        agent_step! = schelling_step!,
        properties,
        rng,
        container = Vector, # agents are not removed, so we us this
        scheduler = Schedulers.Randomly() # all agents are activated once at random
    )

    # populate the model with agents, adding equal amount of the two types of agents
    # at random positions in the model. At the start all agents are unhappy.
    for n in 1:total_agents
        add_agent_single!(model; mood = false, group = n < total_agents / 2 ? 1 : 2)
    end

    return model

end

schelling = initialize()

groupcolor(a) = a.group == 1 ? :blue : :orange
groupmarker(a) = a.group == 1 ? :circle : :rect

abmvideo(
    "schelling.mp4", schelling;
    agent_color = groupcolor, agent_marker = groupmarker, agent_size = 10,
    framerate = 8, frames = 1000,
    title = "Schelling's segregation model"
)