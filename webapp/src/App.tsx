import { Button, Center, Flex, Heading, Image, Input, Slider, Text } from "@chakra-ui/react"
import { useEffect, useRef, useState } from "react"
import { FaFastBackward, FaFastForward, FaGithub, FaPlay, FaPlayCircle } from "react-icons/fa"
import { LuChefHat } from "react-icons/lu"

export default function Page() {
	const [boxHeight, setBoxHeight] = useState<number>(0)

	const [generating, setGenerating] = useState(false)
	const [ws, setWs] = useState<WebSocket>()
	const audioCtxRef = useRef(null)
	const bufferQueueRef = useRef(Promise.resolve())

	function handleBoxRef(ref: HTMLDivElement) {
		if (!ref) return
		setBoxHeight(ref.clientWidth)
	}

	useEffect(() => {
		if (!generating) return
		// Audio context init
		audioCtxRef.current = new (window.AudioContext)()

		const socket = new WebSocket('ws://localhost:8765/ws')
		socket.binaryType = 'arraybuffer'

		socket.onopen = () => {
			console.log("Websocket connected")
			socket.send("Hello, this is a real-time TTS test!")
		}

		socket.onmessage = (event) => {
			console.log("Recived messsage from server")
			if (typeof event.data === 'string' && event.data === 'END') {
				if (event.data === 'END')
					console.log('Stream ended')
				return
			}
			playChunk(new Float32Array(event.data))
		}
		socket.onerror = (err) => console.error("WS error", err);
		socket.onclose = () => {
			console.log("WebSocket closed")
			setGenerating(false)
		}

		setWs(socket);

		return () => {
			socket.close();
			audioCtxRef.current!.close();
		};
	}, [generating])

	function playChunk(float32Array: Float32Array) {
		if (!audioCtxRef.current) return
		const audioCtx = audioCtxRef.current;
		// create a buffer of 1 channel
		const buf = audioCtx.createBuffer(
			1,
			float32Array.length,
			24000
		);
		buf.copyToChannel(float32Array, 0);

		const source = audioCtx.createBufferSource();
		source.buffer = buf;
		source.connect(audioCtx.destination);

		// ensure chunks play in sequence
		bufferQueueRef.current = bufferQueueRef.current.then(() => {
			return new Promise((resolve) => {
				source.onended = resolve;
				source.start();
			});
		});
	}

	const sendText = (text) => {
		if (ws && ws.readyState === WebSocket.OPEN) ws.send(text);
	}

	return (
		<Flex
			flexDir='column'
			w='100vw'
			h='100vh'
			minH={0}
			fontFamily=''
			background='gray.subtle'
		>
			<Flex
				flexDir='row'
				padding={3}
				fontSize='3xl'
			>
				<Flex flex={1} />
				<Flex flexDir='row'>
					<Text> The Ramsay Expirience </Text>
				</Flex>
				<Flex
					flex={1}
					flexDir='row'
					alignItems='center'
					justifyContent='end'
				>
					<FaGithub />
				</Flex>
			</Flex>
			<Center
				flex={1}
				w='100%'
				pos='relative'
				flexDir='column'
			>
				<Image
					src='ramsay.png'
					objectFit='contain'
					zIndex={0}
					width={`${boxHeight}px`}
				/>
				<Center
					flexDir='column'
					gap={2}
					padding={5}
					shadow='2xl'
					shadowColor='fg'
					fontSize={23}
					borderRadius={20}
					border='solid'
					borderWidth={1}
					borderColor='gray.200'
					zIndex={1}
					bg='bg'
					ref={handleBoxRef}
				>
					<Text> "Thow it in a mixer idiot sandwiwich" </Text>
					<Center flexDir='row' gap={2}>
						<FaFastBackward />
						<FaPlayCircle size={40} />
						<FaFastForward />
					</Center>
					<Slider.Root w='70%'>
						<Slider.Control>
							<Slider.Track>
								<Slider.Range />
							</Slider.Track>
							<Slider.Thumbs />
						</Slider.Control>
					</Slider.Root>
					<Flex flexDir='row' gap={2}>
						<Input
							flex={1}
							placeholder='URL to Recipe'
						/>
						<Button
							onClick={() => {
								setGenerating(true)
								sendText("Hello you silly person")
							}}
						>
							<LuChefHat />
							Start Cooking
						</Button>
					</Flex>
				</Center>
			</Center>
		</Flex>
	)
}
