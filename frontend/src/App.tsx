import { useState } from 'react'
import { Button, FileInput, NativeSelect, Paper, SimpleGrid, Stack, Text, Table, Container, Title } from '@mantine/core'

type NoteResult = {
  position: number
  status: 'paired' | 'missing' | 'extra'
  expected: string | null
  played: string | null
  pitch_correct?: boolean
  timing_correct?: boolean
  duration_correct?: boolean
  velocity_correct?: boolean
}

type AnalysisReport = {
  overall_score: number
  pitch_score: number
  timing_score: number
  duration_score: number
  velocity_score: number
  note_results: NoteResult[]
}

function App() {
  const [referenceFile, setReferenceFile] = useState<File | null>(null)
  const [studentFile, setStudentFile] = useState<File | null>(null)
  const [report, setReport] = useState<AnalysisReport | null>(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [resultLabel, setResultLabel] = useState('')
  const [referenceSource, setReferenceSource] = useState('upload')

  async function analyzeFiles(reference: File, student: File) {

    setIsLoading(true)
    setError('')
    setReport(null)

    const formData = new FormData()
    formData.append('reference_file', reference)
    formData.append('student_file', student)

    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Analysis failed.'
        )
      }

      setReport(data)
    } catch (caught) {
      setError(
        caught instanceof Error ? caught.message : 'Something went wrong.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  async function handleAnalyze() {
    if (!studentFile || isLoading) return
    if (referenceSource === 'upload' && !referenceFile) return

    setIsLoading(true)
    setError('')
    setReport(null)

    try {
      let reference = referenceFile

      if (referenceSource === 'scale') {
        const response = await fetch('/samples/reference_scale.mid')

        if (!response.ok) {
          throw new Error('Could not load the reference exercise.')
        }

        reference = new File(
          [await response.blob()],
          'reference_scale.mid',
          { type: 'audio/midi' }
        )
      }

      if (!reference) {
        throw new Error('Please select a reference MIDI file.')
      }

      setResultLabel(
        referenceSource === 'scale'
          ? 'Included C major scale compared with your performance'
          : 'Your uploaded performance'
      )

      await analyzeFiles(reference, studentFile)
    } catch (caught) {
      setError(
        caught instanceof Error ? caught.message : 'Analysis failed.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  async function handleExample() {
    if (isLoading) return

    setIsLoading(true)
    setError('')
    setReport(null)
    setResultLabel('Example: C major scale with pitch and timing mistakes')

    try {
      const [referenceResponse, studentResponse] = await Promise.all([
        fetch('/samples/reference_scale.mid'),
        fetch('/samples/student_scale.mid'),
      ])

      if (!referenceResponse.ok || !studentResponse.ok) {
        throw new Error('Could not load the example files.')
      }

      const [referenceBlob, studentBlob] = await Promise.all([
        referenceResponse.blob(),
        studentResponse.blob(),
      ])

      const reference = new File(
        [referenceBlob],
        'reference_scale.mid',
        { type: 'audio/midi' }
      )

      const student = new File(
        [studentBlob],
        'student_scale.mid',
        { type: 'audio/midi' }
      )

      await analyzeFiles(reference, student)
    } catch (caught) {
      setError(
        caught instanceof Error ? caught.message : 'Could not run the example.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main>
      <Container size="lg" py="xl" ta="center">
        <Title order={1} mb="xs">
          MIDI Performance Analyzer
        </Title>

        <Text c="dimmed" mb="xl">
          Compare your performance against a reference MIDI file.
        </Text>

        <Stack gap="sm" maw={480} mx="auto" ta="left">
          <NativeSelect
            label="Reference exercise"
            value={referenceSource}
            disabled={isLoading}
            data={[
              { value: 'upload', label: 'Upload my own reference' },
              { value: 'scale', label: 'Included C major scale' },
            ]}
            onChange={(event) => {
              setReferenceSource(event.currentTarget.value)
              setReferenceFile(null)
              setReport(null)
              setError('')
            }}
          />

          {referenceSource === 'upload' && (
            <FileInput
              label="Reference MIDI file"
              placeholder="Choose a reference MIDI file"
              accept=".mid,.midi"
              value={referenceFile}
              onChange={setReferenceFile}
              disabled={isLoading}
            />
          )}

          <FileInput
            label="Student MIDI file"
            placeholder="Choose your performance MIDI file"
            accept=".mid,.midi"
            value={studentFile}
            onChange={setStudentFile}
            disabled={isLoading}
          />
        </Stack>

        <Button
          type="button"
          onClick={handleAnalyze}
          loading={isLoading}
          disabled={
            isLoading ||
            !studentFile ||
            (referenceSource === 'upload' && !referenceFile)
          }
          mt="md"
        >
          Analyze performance
        </Button>

        <p>No MIDI files handy? Try an included example.</p>

        <Button
          type="button"
          variant="light"
          onClick={handleExample}
          disabled={isLoading}
        >
          Try an example
        </Button>

        {error && <p role="alert">{error}</p>}

        {report !== null && (
          <section>
            <h2>Performance scores</h2>
            <p>{resultLabel}</p>
            <SimpleGrid cols={{ base: 1, sm: 2, md: 5 }} mt="md" mb="xl">
              {[
                { label: 'Overall', value: report.overall_score },
                { label: 'Pitch', value: report.pitch_score },
                { label: 'Timing', value: report.timing_score },
                { label: 'Duration', value: report.duration_score },
                { label: 'Velocity', value: report.velocity_score },
              ].map((score) => (
                <Paper key={score.label} withBorder p="md" radius="md">
                  <Text size="sm" c="dimmed">
                    {score.label}
                  </Text>
                  <Text size="xl" fw={700}>
                    {score.value.toFixed(1)}%
                  </Text>
                </Paper>
              ))}
            </SimpleGrid>

            <h3>Note feedback</h3>
            <Table.ScrollContainer minWidth={800}>
              <Table
                striped
                highlightOnHover
                withTableBorder
                horizontalSpacing="md"
                verticalSpacing="sm"
              >
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th scope="col">Position</Table.Th>
                    <Table.Th scope="col">Expected</Table.Th>
                    <Table.Th scope="col">Played</Table.Th>
                    <Table.Th scope="col">Pitch / alignment</Table.Th>
                    <Table.Th scope="col">Timing</Table.Th>
                    <Table.Th scope="col">Duration</Table.Th>
                    <Table.Th scope="col">Velocity</Table.Th>
                  </Table.Tr>
                </Table.Thead>

                <Table.Tbody>
                  {report.note_results.map((note) => (
                    <Table.Tr key={note.position}>
                      <Table.Td>{note.position}</Table.Td>
                      <Table.Td>{note.expected ?? '—'}</Table.Td>
                      <Table.Td>{note.played ?? '—'}</Table.Td>
                      <Table.Td>
                        {note.status === 'missing'
                          ? 'Missing note'
                          : note.status === 'extra'
                            ? 'Extra note'
                            : note.pitch_correct
                              ? 'Correct pitch'
                              : 'Incorrect pitch'}
                      </Table.Td>

                      <Table.Td>
                        {note.status !== 'paired'
                          ? '—'
                          : note.timing_correct
                            ? 'On time'
                            : 'Outside tolerance'}
                      </Table.Td>

                      <Table.Td>
                        {note.status !== 'paired'
                          ? '—'
                          : note.duration_correct
                            ? 'Correct'
                            : 'Outside tolerance'}
                      </Table.Td>

                      <Table.Td>
                        {note.status !== 'paired'
                          ? '—'
                          : note.velocity_correct
                            ? 'Correct'
                            : 'Outside tolerance'}
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </Table.ScrollContainer>
          </section>
        )}
      </Container>
    </main>
  )
}

export default App
